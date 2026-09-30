from pathlib import Path
import pytest
from labcore.config import load_config
from labcore.runtime import CommandResult
from engine import Policy,assess,run_job,PRESETS,DEFAULT_CSV

@pytest.fixture
def config(): return load_config(Path(__file__).resolve().parents[1])[0]

def test_preview_never_executes_code(config,tmp_path):
    target=tmp_path/'sentinel'
    result=assess(f'open({str(target)!r},"w").write("unsafe")',config)
    assert result['syntax_valid']
    assert not target.exists()

@pytest.mark.parametrize('field,value',[('cpus',0),('memoryMb',99999),('timeoutSeconds',0),('network','default'),('image','unreviewed/image')])
def test_policy_rejects_unsafe_settings(config,field,value):
    with pytest.raises(ValueError): Policy.model_validate(dict(config,**{field:value}))

def test_missing_runtime_does_not_execute_on_host(config,monkeypatch,tmp_path):
    target=tmp_path/'sentinel'
    monkeypatch.delenv('CONTAINER_BIN',raising=False)
    monkeypatch.setattr('labcore.runtime.shutil.which',lambda _:None)
    with pytest.raises(RuntimeError,match='not installed'):
        run_job(f'open({str(target)!r},"w").write("bad")',DEFAULT_CSV,'data.csv',config)
    assert not target.exists()

def test_input_mounts_and_network_are_explicit(config,monkeypatch):
    class Runtime:
        def require(self): pass
        def run(self,image,argv,**kw):
            assert kw['network']=='none'
            assert kw['user']=='65534:65534'
            assert all(m[2]=='ro' for m in kw['mounts'])
            assert Path(kw['mounts'][0][0],'data.csv').read_bytes()==DEFAULT_CSV
            return CommandResult(0,'{"count":3}\n','',.2,'completed')
    monkeypatch.setattr('engine.AppleContainer',Runtime)
    assert run_job(PRESETS['Analyze CSV'],DEFAULT_CSV,'data.csv',config)['passed']

def test_input_path_traversal_rejected(config):
    with pytest.raises(ValueError,match='filename'): run_job('print(1)',b'', '../escape',config)

def test_input_size_limit(config):
    with pytest.raises(ValueError,match='budget'): run_job('print(1)',b'x'*(config['maxInputBytes']+1),'data.csv',config)

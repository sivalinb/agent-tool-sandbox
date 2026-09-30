from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from labcore.config import load_config
from labcore.observability import Recorder
config,meta=load_config(ROOT)
parser=argparse.ArgumentParser()
parser.add_argument('--live',action='store_true')
recorder=Recorder(ROOT,ROOT.name)
with recorder.span('cli_run'):
    from engine import assess,run_job,security_evaluation,PRESETS,DEFAULT_CSV
    parser.add_argument('--security-eval',action='store_true')
    args=parser.parse_args()
    if args.security_eval and not args.live: parser.error('--security-eval requires --live')
    report=security_evaluation(config) if args.security_eval else run_job(PRESETS['Analyze CSV'],DEFAULT_CSV,'data.csv',config) if args.live else assess(PRESETS['Analyze CSV'],config)
report['config_provenance']=meta
recorder.save(report)
(ROOT/'artifacts/cli-latest.json').write_text(json.dumps(report,indent=2,allow_nan=False))
print(json.dumps(report,indent=2,allow_nan=False))
if report.get('passed') is False: raise SystemExit(1)

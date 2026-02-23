
import traceback
try:
    # TouchDesigner内実行を想定するためのスクリプト
    polish = op('/project1/polish_test')
    if not polish:
        print('Error: polish_test not found')
    else:
        with open('scripts/deploy_cyber_clock.py', 'r', encoding='utf-8') as script_file:
            exec(script_file.read())
        print('Deployment script sent to TD.')
except Exception as e:
    print(f'Execution error: {e}')

import os
import subprocess
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Define a BashScriptRunner class


class BashScriptRunner:
    def __init__(self, script_path):
        # Save the path to the script as an instance variable
        self.script_path = script_path

    def run_script(self):
        # Construct a command to execute the script
        command = f'bash {self.script_path}'

        # Execute the command and capture its output
        output = subprocess.check_output(command, shell=True)

        # Decode the output from bytes to a UTF-8 string and return it
        return output.decode('utf-8')


if __name__ == '__main__':
    SCRIPT = os.environ.get('SCRIPT')
    # Example usage
    runner = BashScriptRunner(SCRIPT)
    output = runner.run_script()
    print(output)

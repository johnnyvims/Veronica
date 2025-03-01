import subprocess

class ReconTool:
    def __init__(self, url):
        self.url = url

    def run_dirsearch(self):
        # Build the command
        command = [
            "dirsearch", 
            "-u", self.url, 
            "-t", "50", 
            "-i", "200"
        ]
        
        # Run the command using subprocess
        subprocess.run(command, check=True)

# Example usage:
#recon = ReconTool("http://take-survey.heal.htb/index.php/")
#recon.run_dirsearch()

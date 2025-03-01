#we need to remove the cewl fucntion, that is going to be in stage2 now

from termcolor import colored

from stage1 import CME_Enumration
from stage2 import FfufAutomation
from thebeast import SlowPrinter

def get_target():
        print(colored("Enter the target address (e.g., http://example.com or IP):", "cyan"))
        target = input(colored("[>] Target: ", "yellow")).strip()
        if not target:
            print(colored("[!] No target provided. Exiting...", "red"))
            sys.exit(1)
        return target

Slow_Print = SlowPrinter()
target = get_target()

First_Stage = CME_Enumration(target)
First_Stage.run_all()

print("\n")
print(colored(f"--------------------------------------------------NOTICE----------------------------------------------------", "yellow"))
print("\n")
Slow_Print.slow_print_with_bg("[!] Stage One Complete!")
print("\n")
print(colored(f"--------------------------------------------------NOTICE----------------------------------------------------", "yellow"))
print("\n")

Secound_Stage= FfufAutomation(target, First_Stage.cms, dev=False)
Secound_Stage.run_recon()

print("\n")
print(colored(f"--------------------------------------------------NOTICE----------------------------------------------------", "yellow"))
print("\n")
Slow_Print.slow_print_with_bg("[!] Stage Two Complete!")
print("\n")
print(colored(f"--------------------------------------------------NOTICE----------------------------------------------------", "yellow"))
print("\n")

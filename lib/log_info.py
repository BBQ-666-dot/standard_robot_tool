def LogInfo(string="") -> None:
    print(f"\033[92mINFO:{string}\033[0m")


def LogWarning(string="") -> None:
    print(f"\033[93mWARNING:{string}\033[0m")


def LogError(string="") -> None:
    print(f"\033[91mERROR:{string}\033[0m")
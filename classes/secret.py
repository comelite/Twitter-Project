class Secret():
    def __init__(self, file="secrets.txt"):
        """Class constructor

        @param file : the path to the file containing the secrets
        """
        with open("secrets.txt", "r") as f:
            secret = f.read().splitlines()
            self.api_key = secret[0].split()[1]
            self.api_secret = secret[1].split()[1]
            self.bearer_token = secret[2].split()[1]
            self.access_token = secret[3].split()[1]
            self.access_token_secret = secret[4].split()[1]

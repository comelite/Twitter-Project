class Secrets():
    # Class to decode a file containing the secrets
    def __init__(self, file = "secrets.txt"):
        # Class constructor
        # @param file : the file containing the secrets
        with open("secrets.txt","r") as f:
            secrets = f.read().splitlines()
            self.api_key = secrets[0].split()[1]
            self.api_secret = secrets[1].split()[1]
            self.bearer_token = secrets[2].split()[1]
            self.access_token = secrets[3].split()[1]
            self.access_token_secret = secrets[4].split()[1]

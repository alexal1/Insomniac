import os

HIDDEN_DIRECTORY = './insomniac/extra_features/'


def generate_stubs():
    for filename in os.listdir(HIDDEN_DIRECTORY):
        if filename.endswith(".py") and not filename == "__init__.py":
            print(f"Generating stub for {filename}...")
            with open(f"{HIDDEN_DIRECTORY}{filename}", 'w') as file:
                module = filename[:-3]
                file.write(f"from insomniac import activation_controller\n\n"
                           f"exec(activation_controller.get_extra_feature('{module}'))\n")


if __name__ == "__main__":
    generate_stubs()

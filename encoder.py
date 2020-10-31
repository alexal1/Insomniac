import base64
import os
import re
import zlib

HIDDEN_DIRECTORY = './insomniac/'
EMPTY_REGEX = r'^\s*$'
IMPORTS_REGEX = r'^from|import [\s\S]+$'


def encode():
    for filename in os.listdir(HIDDEN_DIRECTORY):
        if filename.endswith(".py") and not filename == "__init__.py":
            print(f"Encoding {filename}...")
            with open(f"{HIDDEN_DIRECTORY}{filename}", 'r') as file:
                code = file.readlines()

            iterating_imports = True
            imports = ""
            code_body = ""
            for line in code:
                if not iterating_imports:
                    code_body += line
                    continue

                empty_match = re.match(EMPTY_REGEX, line)
                imports_match = re.match(IMPORTS_REGEX, line)

                if empty_match is not None or imports_match is not None:
                    imports += line
                else:
                    code_body += line
                    iterating_imports = False

            code_body_obfuscated = base64.b64encode(zlib.compress(code_body.encode('utf-8')))

            final_code = f"{imports}import base64\nimport zlib\n\ncode = " \
                         f"zlib.decompress(base64.b64decode({code_body_obfuscated}))\nexec(code)\n"
            with open(f"{HIDDEN_DIRECTORY}{filename}", 'w') as file:
                file.write(final_code)


if __name__ == "__main__":
    encode()

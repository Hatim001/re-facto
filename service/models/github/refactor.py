import ast
import base64

import openai
import requests
from django.conf import settings
from github import Github

from account.proxies.github_account import GitHubAccount


class GithubRefactorService:
    """
    A class used to refactor code snippets in a given commit.

    Attributes:
        account (GitHubAccount): A GitHub account object.
        commit (dict): A dictionary containing commit information.
        g (Github): A Github object.
        file_changes (List[Dict[str, List[str]]]): A list of dictionaries containing filename and corresponding file blocks.
    """

    def __init__(self, account: GitHubAccount, commit: dict):
        """
        Constructs all the necessary attributes for the GithubRefactorService object.

        Args:
            account (GitHubAccount): A GitHub account object.
            commit (dict): A dictionary containing commit information.
        """
        self.account = account
        self.commit = commit
        self.g = Github(account.access_token)
        openai.api_key = settings.OPENAI_API_KEY

    def get_file_changes(self):
        """
        Get changes in files from the commit.

        Returns:
            list: A list of dictionaries containing filename and corresponding file blocks.
        """
        file_changes = []
        if not self.commit.get("files"):
            return file_changes

        for file_info in self.commit.get("files"):
            if self.is_file_modified_or_added(file_info):
                file_blocks = self.get_file_blocks(file_info)
                file_changes.append({file_info["filename"]: file_blocks})

        return file_changes

    def is_file_modified_or_added(self, file_info):
        """
        Check if the file is modified or added.

        Args:
            file_info (dict): A dictionary containing file information.

        Returns:
            bool: True if the file is modified or added, False otherwise.
        """
        return (file_info["status"] in ["modified", "added"]) and file_info[
            "additions"
        ] > self.max_lines

    def get_file_blocks(self, file_info):
        """
        Get file blocks for the given file.

        Args:
            file_info (dict): A dictionary containing file information.

        Returns:
            list: A list of file blocks.
        """
        file_content = self.get_full_file(file_info["contents_url"])
        file_blocks = [file_content]
        changed_blocks = self.get_changed_blocks(file_info["patch"])
        file_blocks.extend("\n".join(change_block) for change_block in changed_blocks)
        return file_blocks

    def get_changed_blocks(self, patch):
        """
        Get changed blocks from the patch.

        Args:
            patch (str): A string representing the patch.

        Returns:
            list: A list of changed blocks.
        """
        lines = patch.split("\n")
        changed_blocks = []
        current_block = []

        for line in lines:
            if line.startswith("@@") and current_block:
                changed_blocks.append(current_block)
                current_block = []
            elif line.startswith("+"):
                current_block.append(line[1:])

        if current_block:
            changed_blocks.append(current_block)

        return changed_blocks

    def get_full_file(self, contents_url):
        """
        Retrieves the full content of a file from the given contents URL.

        Args:
            contents_url (str): The URL to retrieve the file content from.

        Returns:
            str: The full content of the file.
        """
        headers = {}
        r = requests.get(contents_url, headers=headers)
        r.raise_for_status()
        data = r.json()
        file_content = data["content"]
        file_content_encoding = data.get("encoding")
        if file_content_encoding == "base64":
            file_content = base64.b64decode(file_content).decode()
        return file_content

    def refactor_change_code(self):
        """
        Refactors the given code snippets to make them smell free and more optimized.
        """
        try:
            openai.api_key = settings.OPENAI_API_KEY
            refactored_file_changes = []
            sample_dictionary = {
                "filename": [
                    "full file code",
                    "snippet 1",
                    "snippet 2",
                    "snippet 3",
                    "snippet 4",
                ]
            }

            refactored_sample_dictionary = {"filename": """full file refactored code"""}

            explain_system_message = {
                "role": "system",
                "content": """ You are a world-class software developer with a knowledge of all programming languages.
                You carefully examine code snippets with great detail and accuracy. Refactor a code according to the instructions given below:
                1. You are provide with full code as well as the snippets of the code which needs to be refactored. Also refactor the code which is asked do not refactor or change the code which is not there code snippet list.
                2. You have full code have look at and understand that in detail. Now refactor only the snippets which are asked to do and it should not change the working of it.
                3. There are many kinds of code smells that you can look upon in the code and remove smells. You can remove smells if you find them in the code but the working of the code should not be changed.
                4. You can change of the function, class or variables if they ar e not relatable to function or class and not according to the naming convention the language.
                5. Format the file for proper indentation after the refactoring and also remove unnecessary comments from te file.
                6. Keep in mind the indentation of the code provided to you. After refactoring it should follow the same indentation as it was in the code provided to you. Keep this thing serious because it can cause error in a lot of programming languages.
                7. If you are not confident about refactoring or optimizing the code then do not do it just keep it as it was before.
                8. Also check if the solid principles for the software development are violated then refactor it if you can solve otherwise do not change it.
                9. In some cases if you feel confused about refactoring then do not change the code.

                These are some points that you need to consider while refactoring the code.

                """,
            }

            for file_change in self.file_changes:
                explain_user_message = {
                    "role": "user",
                    "content": f""" Refactor the given code snippets to make them smell free and more optimized.
                    If a snippet is correct and does not need any changes, Just don't change it.
                    I have given you the sample dictionary which I will provide to you as a input.
                    Now in dictionary the key value is a file name and value is the list.
                    Now the first element of the list is the full code of the file. Now understand that code properly and
                    from second element i.e. index 1 all are the code snippet that are need to be refactored in the full code.
                    First find the code snippet in the full code and then do the refactoring. While finding in full code match it exactly.
                    There can be a multiple snippets to refactor in the full code. And do not change the code other than that in full code.
                    What will the dictionary look like is given below as a example:
                    ```
                    {sample_dictionary}
                    ```
                    Just take up each snippet and refactor it according to the instructions points given to you.
                    After you have refactored all the code snippet in full file code then give me that refactored full file code
                    in the format I have asked for. It should follow the indentation of the file as it was before in non changed file.
                    And given a response according to the Python dictionary format is given below:
                    ```
                    {refactored_sample_dictionary}
                    ```
                    In the dictionary add the refactored full code and if you haven't refactored the any code snippet in the full file code just
                    give me the original full file code. And remove all the code snippet and just give the full code as the string value against the filename key in the dictionary.
                    There should be only string value that contains full code. Consider this point strictly. As your response has lot of dependency.

                    Now here is my Python dictionary for refactoring the snippets of the code in the full code:
                    ```
                    {file_change}
                    ```
                    Give a response according to the instructions I gave you.
                    Please generate a full refactored code dont stop in between. And give me only the dictionary as string so that I can convert directly to python dictionary.
                    Complete the whole response with the dictionary parenthesis dont leave the string value incomplete as it affects my further processing.

                    """,
                }
                prompt_messages = [explain_system_message, explain_user_message]
                llm_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=prompt_messages,
                    temperature=1.0,
                )
                code = llm_response["choices"][0]["message"]["content"]
                try:
                    refactored_file_change = ast.literal_eval(code)
                    refactored_file_changes.append(refactored_file_change)
                except Exception:
                    for filename, code in file_change.items():
                        refactored_file_change = {filename: code[0]}
                        refactored_file_changes.append(refactored_file_change)
            return refactored_file_changes
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []

    def refactor(self, max_lines):
        self.max_lines = max_lines
        self.file_changes = self.get_file_changes()
        return self.refactor_change_code() if self.file_changes else False

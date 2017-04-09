from abc import abstractmethod

from hardening import core, io
from hardening.utils import HardeningUtil


class CommandUtil(HardeningUtil):
    """
    parent class for all utils executing commands
    prompts the user whether he wants to run the command or not
    """

    def get_transaction_key(self):
        return "cmd:%s" % (id(self))

    # def get_transaction_kwargs(self):
    #    return {storage.CommandTransaction.COMMIT_KEY: self.get_commit_command(),
    # storage.CommandTransaction.ROLLBACK_KEY: self.get_rollback_command()}

    @abstractmethod
    def get_commit_command(self):
        return []

    @abstractmethod
    def get_rollback_command(self):
        return []

    def __setup__(self):
        pass

    def __run__(self):
        __run_cmd = True
        if core.RuntimeOptions().interactive_mode():
            __run_cmd = io.create_writer().prompt_user_yesnocancel(
                _("Do you want to run the following command"),
                quoted=[" ".join(self.get_commit_command())])

        if __run_cmd:
            self.transaction().set_commit_command(self.get_commit_command())
            self.transaction().set_rollback_command(self.get_rollback_command())

    def __finish__(self):
        pass

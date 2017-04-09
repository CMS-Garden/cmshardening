# This file is part of BSICMS2.
#
# BSICMS2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import inspect
import os
from abc import ABCMeta, abstractmethod
from collections import namedtuple

from six import with_metaclass

from hardening import io, core


# pylint: disable=too-few-public-methods
class TransactionStatus(object):
    """
    helper class holding all possible transaction statuses
    """
    NEW = "NEW"
    RUNNING = "RUNNING"
    COMMITPREPARED = "COMMITPREPARED"
    COMMITTED = "COMITTED"
    ROLLEDBACK = "ROLLEDBACK"


class Transaction(with_metaclass(ABCMeta)):
    """
    parent class for all transaction
    manages transaction state changes and some simple I/O
    """

    def __init__(self, url):
        self.__status = TransactionStatus.NEW
        self.__writer = io.create_writer()
        self.__has_modifications = False
        self.__url = url
        self.__change_commands = list()

        operation = namedtuple(
            'operation', ['action', 'condition', 'next_state'])

        self.__transaction_statechanges = {
            TransactionStatus.NEW: {
                self.begin:
                    operation(action=self.__begin__,
                              condition=None,
                              next_state=TransactionStatus.RUNNING),
                self.prepare_commit:
                    operation(action=None,
                              condition=lambda: not self.has_something_to_commit(),
                              next_state=TransactionStatus.NEW),
                self.commit:
                    operation(action=None,
                              condition=None,
                              next_state=TransactionStatus.COMMITTED),
                self.rollback:
                    operation(action=None,
                              condition=None,
                              next_state=TransactionStatus.ROLLEDBACK)
            },
            TransactionStatus.RUNNING: {
                self.begin:
                    operation(action=None,
                              condition=None,
                              next_state=TransactionStatus.RUNNING),
                self.prepare_commit:
                    operation(action=self.__prepare_commit__,
                              condition=None,
                              next_state=TransactionStatus.COMMITPREPARED),
                self.rollback:
                    operation(action=self.__rollback__,
                              condition=None,
                              next_state=TransactionStatus.ROLLEDBACK)
            },
            TransactionStatus.COMMITPREPARED: {
                self.commit:
                    operation(action=self.__commit__,
                              condition=None,
                              next_state=TransactionStatus.COMMITTED),
                self.rollback:
                    operation(action=self.__rollback__,
                              condition=None,
                              next_state=TransactionStatus.ROLLEDBACK)
            },
            # the transition from committed to rolledback is required enable the TransactionManager
            # to roll back all transitions, independant of their state. A Transaction should
            # do a full cleanup during the commit operation as well as the
            # rollback operation
            TransactionStatus.COMMITTED: {
                self.rollback:
                    operation(action=self.__rollback__,
                              condition=None,
                              next_state=TransactionStatus.ROLLEDBACK)
            },
            TransactionStatus.ROLLEDBACK: {
            }
        }

    def url(self):
        return self.__url

    def add_change_command(self, cmd):
        self.__change_commands.append(cmd)

    def is_transaction_running(self):
        return self.__status == TransactionStatus.RUNNING

    def begin(self):
        self.__change_state()

    def prepare_commit(self):
        self.__change_state()

    def commit(self):
        if core.RuntimeOptions().difference_mode() and len(self.__change_commands) > 0:
            if not io.create_writer().prompt_user_yesnocancel(
                    _("Do you want to run the following command(s)?"),
                    quoted=self.__change_commands):
                self.__status = TransactionStatus.COMMITTED
                return

        if core.RuntimeOptions().is_log_enabled():
            for cmd in self.__change_commands:
                core.ChangeLog().append_log_item(cmd)

        self.__has_modifications |= (len(self.__change_commands) > 0)
        self.__change_state()

    def rollback(self):
        self.__change_state()

    def __change_state(self):
        current_status = self.__transaction_statechanges[self.status()]
        current_frame = inspect.currentframe()

        calling_frame = inspect.getframeinfo(
            inspect.getouterframes(current_frame, 2)[1][0])
        try:
            operation = current_status[getattr(self, calling_frame.function)]
        except KeyError:
            raise RuntimeError(
                _("invalid transaction state change: %(status)s --(%(function)s)-> ??")
                % {'status': self.__status, 'function': calling_frame.function})

        if operation.condition is None or operation.condition():
            if operation.action is not None:
                operation.action()
            self.__status = operation.next_state

    def prompt_user(self, message="", quoted=None):
        return self.__writer.prompt_user_yesnocancel(message, quoted=quoted)

    def inform_user(self, message=""):
        """ inform the util whether the changes were made or not """
        if self.url() is not None:
            self.__writer.display_message(os.linesep)
            return self.__writer.display_message(
                message=message, headline=None)

    @staticmethod
    def __get_executing_util():
        for frame in inspect.stack():
            if 'self' in frame[0].f_locals:
                cls = frame[0].f_locals['self'].__class__
                if "HardeningUtil" in [
                        x.__name__ for x in inspect.getmro(cls)]:
                    return frame[0].f_locals['self']
        raise RuntimeError("no util found in stack: %s" % inspect.stack())

    def status(self):
        return self.__status

    def mark_as_modified(self):
        self.__has_modifications = True

    def has_something_to_commit(self):
        return self.__has_modifications

    def has_modifications_to_save(self):
        return self.__has_modifications

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.url() == other.url()

    def __hash__(self):
        return hash(self.__class__)

    def __str__(self):
        return str(self.url_schema()) + ":" + str(self.url())

    @abstractmethod
    def __begin__(self):
        pass

    @abstractmethod
    def __prepare_commit__(self):
        pass

    @abstractmethod
    def __commit__(self):
        pass

    @abstractmethod
    def __rollback__(self):
        pass

    @staticmethod
    def url_schema():
        return None

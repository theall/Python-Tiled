##
# commandlineparser.py
# Copyright 2011, Ben Longbons
# Copyright 2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
#
# This file is part of Tiled.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
##

from pyqtcore import QChar, QString, QVector, QStringList, QList
from PyQt5.QtCore import (
    QFileInfo,
    QCoreApplication,
    qWarning
)

##
# C-style callback function taking an arbitrary data pointer.
##
def Callback():
    pass

##
# A template function that will static-cast the given \a object to a type T
# and call the member function of T given in the second template argument.
##
def MemberFunctionCall(object):
    t = object
    t.memberFunction()

##
# A simple command line parser. Options should be registered through
# registerOption().
#
# The help option (-h/--help) is provided by the parser based on the
# registered options.
##
class CommandLineParser():
    def __init__(self):
        self.mCurrentProgramName = QString()
        self.mOptions = QVector()
        self.mShowHelp = False
        self.mLongestArgument = 0
        self.mFilesToOpen = QStringList()

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('CommandLineParser', sourceText, disambiguation, n)

    def trUtf8(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('CommandLineParser', sourceText, disambiguation, n)

    ##
    # Registers an option with the parser. When an option with the given
    # \a shortName or \a longName is encountered, \a callback is called with
    # \a data as its only parameter.
    ##
    def registerOption(self, *args):
        l = len(args)
        if l==4:
            ##
            # Convenience overload that allows registering an option with a callback
            # as a member function of a class. The class type and the member function
            # are given as template parameters, while the instance is passed in as
            # \a handler.
            #
            # \overload
            ##
            handler, shortName, longName, help = args
            self.registerOption(MemberFunctionCall, handler, shortName, longName, help)
        elif l==5:
            callback, data, shortName, longName, help = args
            self.mOptions.append(CommandLineParser.Option(callback, data, shortName, longName, help))
            length = longName.length()
            if (self.mLongestArgument < length):
                self.mLongestArgument = length

    ##
    # Parses the given \a arguments. Returns False when the application is not
    # expected to run (either there was a parsing error, or the help was
    # requested).
    ##
    def parse(self, arguments):
        self.mFilesToOpen.clear()
        self.mShowHelp = False
        todo = QStringList(arguments)
        self.mCurrentProgramName = QFileInfo(todo.takeFirst()).fileName()
        index = 0
        noMoreArguments = False
        while (not todo.isEmpty()):
            index += 1
            arg = todo.takeFirst()
            if (arg.isEmpty()):
                continue
            if (noMoreArguments or arg.at(0) != '-'):
                self.mFilesToOpen.append(arg)
                continue

            if (arg.length() == 1):
                # Traditionally a single hyphen means read file from stdin,
                # write file to stdout. This isn't supported right now.
                qWarning(self.tr("Bad argument %d: lonely hyphen"%index))
                self.showHelp()
                return False

            # Long options
            if (arg.at(1) == '-'):
                # Double hypen "--" means no more options will follow
                if (arg.length() == 2):
                    noMoreArguments = True
                    continue

                if (not self.handleLongOption(arg)):
                    qWarning(self.tr("Unknown long argument %d: %s"%(index, arg)))
                    self.mShowHelp = True
                    break

                continue

            # Short options
            for i in range(1, arg.length()):
                c = arg.at(i)
                if (not self.handleShortOption(c)):
                    qWarning(self.tr("Unknown short argument %d.%d: %s"%(index, i, c)))
                    self.mShowHelp = True
                    break

        if (self.mShowHelp):
            self.showHelp()
            return False

        return True

    ##
    # Returns the files to open that were found among the arguments.
    ##
    def filesToOpen(self):
        return QList(self.mFilesToOpen)

    def showHelp(self):
        qWarning(self.tr("Usage:\n  %s [options] [files...]"%self.mCurrentProgramName) + "\n\n" + self.tr("Options:"))
        qWarning("  -h %-*s : %s", self.mLongestArgument, "--help", self.tr("Display this help"))
        for option in self.mOptions:
            if (not option.shortName.isNull()):
                qWarning("  -%c %-*s : %s",
                         option.shortName.toLatin1(),
                         self.mLongestArgument, option.longName,
                         option.help)
            else:
                qWarning("     %-*s : %s",
                         self.mLongestArgument, option.longName,
                         option.help)

        qWarning()

    def handleLongOption(self, longName):
        if (longName == "--help"):
            self.mShowHelp = True
            return True

        for option in self.mOptions:
            if (longName == option.longName):
                option.callback(option.data)
                return True

        return False

    def handleShortOption(self, c):
        if (c == 'h'):
            self.mShowHelp = True
            return True

        for option in self.mOptions:
            if (c == option.shortName):
                option.callback(option.data)
                return True

        return False

    ##
    # Internal definition of a command line option.
    ##
    class Option():
        def __init__(self, *args):
            l = len(args)
            callback = Callback()
            shortName = QChar()
            longName = QString()
            help = QString()
            if l==0:
                self.callback = 0
                self.data = 0
            elif l==5:
                callback = args[0]
                data = args[1]
                shortName = args[2]
                longName = args[3]
                help = args[4]
                self.callback = callback
                self.data = data
                self.shortName = shortName
                self.longName = longName
                self.help = help

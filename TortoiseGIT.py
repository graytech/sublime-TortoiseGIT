import sublime
import sublime_plugin
import os
import os.path
import subprocess

class TortoiseGitCommand(sublime_plugin.WindowCommand):
	def run(self, cmd, paths=None, isHung=False):
		dir = self.getPath(paths)

		if not dir:
			return
			
		settings = sublime.load_settings('TortoiseGIT.sublime-settings')
		tortoiseproc_path = settings.get('tortoiseproc_path')

		if not os.path.isfile(tortoiseproc_path):
			sublime.error_message(''.join(['can\'t find TortoiseGitProc.exe,',
				' please config setting file', '\n   --sublime-TortoiseGIT']))
			raise

		proce = subprocess.Popen('"' + tortoiseproc_path + '"' + 
			' /command:' + cmd + ' /path:"%s"' % dir , stdout=subprocess.PIPE)

		# This is required, cause of ST must wait TortoiseSVN update then revert
		# the file. Otherwise the file reverting occur before SVN update, if the
		# file changed the file content in ST is older.
		if isHung:
			proce.communicate()

	def getPath(self, paths):
		path = None
		if paths:
			path = '*'.join(paths)
		else:
			view = sublime.active_window().active_view()
			path = view.file_name() if view else None

		return path


class MutatingTortoiseGitCommand(TortoiseGitCommand):
	def run(self, cmd, paths=None):
		TortoiseGitCommand.run(self, cmd, paths, True)
		
		self.view = sublime.active_window().active_view()
		(row,col) = self.view.rowcol(self.view.sel()[0].begin())
		self.lastLine = str(row + 1);
		sublime.set_timeout(self.revert, 100)

	def revert(self):
		self.view.run_command('revert')
		sublime.set_timeout(self.revertPoint, 600)

	def revertPoint(self):
		self.view.window().run_command('goto_line',{'line':self.lastLine})


class GitUpdateCommand(MutatingTortoiseGitCommand):
	def run(self, paths=None):
		settings = sublime.load_settings('TortoiseGIT.sublime-settings')
		closeonend = '3' if True == settings.get('autoCloseUpdateDialog') else '0'
		MutatingTortoiseGitCommand.run(self, 'update /closeonend:'+closeonend, paths)


class GitCommitCommand(TortoiseGitCommand):
	def run(self, paths=None):
		TortoiseGitCommand.run(self, 'commit', paths)


class GitRevertCommand(MutatingTortoiseGitCommand):
	def run(self, paths=None):
		MutatingTortoiseGitCommand.run(self, 'revert', paths)

class GitPushCommand(MutatingTortoiseGitCommand):
	def run(self, paths=None):
		MutatingTortoiseGitCommand.run(self, 'push', paths)

class GitPullCommand(MutatingTortoiseGitCommand):
	def run(self, paths=None):
		MutatingTortoiseGitCommand.run(self, 'pull', paths)

class GitLogCommand(TortoiseGitCommand):
	def run(self, paths=None):
		TortoiseGitCommand.run(self, 'log', paths)


class GitDiffCommand(TortoiseGitCommand):
	def run(self, paths=None):
		TortoiseGitCommand.run(self, 'diff', paths)


class GitBlameCommand(TortoiseGitCommand):
	def run(self, paths=None):
		TortoiseGitCommand.run(self, 'blame', paths)

	def is_visible(self, paths=None):
		file = self.getPath(paths)
		return os.path.isfile(file) if file else False

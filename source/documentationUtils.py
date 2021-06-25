# -*- coding: UTF-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2006-2021 NV Access Limited, Łukasz Golonka
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import os
import sys

import globalVars
import languageHandler


def getDocFilePath(fileName, localized=True, addon=None):
	if not getDocFilePath.rootPath or not getDocFilePath.addonRootPath:
		if hasattr(sys, "frozen"):
			getDocFilePath.rootPath = os.path.join(globalVars.appDir, "documentation")
		else:
			getDocFilePath.rootPath = os.path.join(globalVars.appDir, "..", "user_docs")
		getDocFilePath.addonRootPath = os.path.join(globalVars.appArgs.configPath, "addons")
	if addon is None:
		rootPath = getDocFilePath.rootPath
	else:
		rootPath = os.path.join(getDocFilePath.addonRootPath, addon, 'doc')

	if localized:
		lang = languageHandler.getLanguage()
		tryLangs = [lang]
		if "_" in lang:
			# This locale has a sub-locale, but documentation might not exist for the sub-locale, so try stripping it.
			tryLangs.append(lang.split("_")[0])
		# If all else fails, use English.
		tryLangs.append("en")

		fileName, fileExt = os.path.splitext(fileName)
		for tryLang in tryLangs:
			tryDir = os.path.join(rootPath, tryLang)
			if not os.path.isdir(tryDir):
				continue

			# Some out of date translations might include .txt files which are now .html files in newer translations.
			# Therefore, ignore the extension and try both .html and .txt.
			for tryExt in ("html", "txt"):
				tryPath = os.path.join(tryDir, f"{fileName}.{tryExt}")
				if os.path.isfile(tryPath):
					return tryPath
		return None
	else:
		# Not localized.
		if not hasattr(sys, "frozen") and fileName in ("copying.txt", "contributors.txt"):
			# If running from source, these two files are in the root dir.
			return os.path.join(globalVars.appDir, "..", fileName)
		else:
			return os.path.join(getDocFilePath.rootPath, fileName)


getDocFilePath.rootPath = None
getDocFilePath.addonRootPath = None

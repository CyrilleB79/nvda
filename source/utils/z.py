# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2023 NV Access Limited, Cyrille Bougot
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import re

# Accelerator syntax: appended at the end of the text, as commonly found in Chinese or Japanese GUIs, e.g. "工具(&T)"
RE_APPENDED_ACCELERATOR = re.compile(r" *\(&.\)$")
# Accelerator syntax as commonly used in Western GUIs, e.g. "&Tools"
RE_INSERTED_ACCELERATOR = re.compile(r"&(?=.)")


def removeAccelerator(text: str) -> str:
	"""Removes the accelerator from a string.
	"""

	text = RE_APPENDED_ACCELERATOR.sub('', text)
	text = RE_INSERTED_ACCELERATOR.sub('', text)
	return text

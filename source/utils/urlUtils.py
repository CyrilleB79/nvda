# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2024 NV Access Limited, Noelia Ruiz Martínez, Leonard de Ruijter

import controlTypes
from urllib.parse import ParseResult, urlparse, urlunparse
from logHandler import log
import textInfos


def getLinkType(targetURL: str, rootURL: str) -> controlTypes.State | None:
	"""Returns the link type corresponding to a given URL.

	:param targetURL: The URL of the link destination
	:param rootURL: The root URL of the page
	:return: A controlTypes.State corresponding to the link type, or C{None} if the state cannot be determined
	"""
	if not targetURL or not rootURL:
		log.debug(f"getLinkType: Either targetUrl {targetURL} or rootUrl {rootURL} is empty.")
		return None
	if isSamePageURL(targetURL, rootURL):
		log.debug(f"getLinkType: {targetURL} is an internal link.")
		return controlTypes.State.INTERNAL_LINK
	log.debug(f"getLinkType: {targetURL} type is unknown.")
	return None


def isSamePageURL(targetURLOnPage: str, rootURL: str) -> bool:
	"""Returns whether a given URL belongs to the same page as another URL.

	:param targetURLOnPage: The URL that should be on the same page as `rootURL`
	:param rootURL: The root URL of the page
	:return: Whether `targetURLOnPage` belongs to the same page as `rootURL`
	"""
	if not targetURLOnPage or not rootURL:
		return False

	validSchemes = ("http", "https", "file")
	# Parse the URLs
	parsedTargetURLOnPage: ParseResult = urlparse(targetURLOnPage)
	if parsedTargetURLOnPage.scheme not in validSchemes:
		return False
	parsedRootURL: ParseResult = urlparse(rootURL)
	if parsedRootURL.scheme not in validSchemes:
		return False

	# Reconstruct URLs without schemes and without fragments for comparison
	targetURLOnPageWithoutFragments = urlunparse(parsedTargetURLOnPage._replace(scheme="", fragment=""))
	rootURLWithoutFragments = urlunparse(parsedRootURL._replace(scheme="", fragment=""))

	fragmentInvalidChars: str = "/"  # Characters not considered valid in fragments
	return targetURLOnPageWithoutFragments == rootURLWithoutFragments and not any(
		char in parsedTargetURLOnPage.fragment for char in fragmentInvalidChars
	)


def _getLinkDataAtCaretPosition(ti: textInfos.TextInfo) -> textInfos._Link | None:
	ti.expand(textInfos.UNIT_CHARACTER)
	obj: NVDAObject = ti.NVDAObjectAtStart
	if obj.role == controlTypes.role.Role.GRAPHIC and (
		obj.parent and obj.parent.role == controlTypes.role.Role.LINK
	):
		# In Firefox, graphics with a parent link also expose the parents link href value.
		# In Chromium, the link href value must be fetched from the parent object. (#14779)
		obj = obj.parent
	if (
		obj.role == controlTypes.role.Role.LINK  # If it's a link, or
		or controlTypes.state.State.LINKED in obj.states  # if it isn't a link but contains one
	):
		return textInfos._Link(
			displayText=obj.name,
			destination=obj.value,
		)
	return None

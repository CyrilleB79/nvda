# -*- coding: UTF-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2021 NV Access Limited, Cyrille Bougot
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import typing
from enum import IntEnum
import weakref
import wx
from logHandler import log


class RefocusableMixin:
	"""A mixin to be used with wx.Dialog to make it refocusable.
	When an instance of a subclass is already opened, trying to create a second instance of the same subclass
	rather focuses the first opened instance.

	To use this dialog:
		* Set L{title} to the title of the dialog.

	@ivar title: The title of the dialog.
	@type title: str
	"""

	class MultiInstanceError(RuntimeError): pass

	class MultiInstanceErrorWithDialog(MultiInstanceError):
		dialog: 'wx.Dialog'

		def __init__(self, dialog: 'RefocusableMixin', *args: object) -> None:
			self.dialog = dialog
			super().__init__(*args)

	class DialogState(IntEnum):
		CREATED = 0
		DESTROYED = 1

	# holds instances of RefocusableMixin as keys, and state as the value
	_instances = weakref.WeakKeyDictionary()
	title = ""

	def __new__(cls, *args, **kwargs):
		# We are iterating over instanceItems only once, so it can safely be an iterator.
		instanceItems = RefocusableMixin._instances.items()
		instancesOfSameClass = (
			(dlg, state) for dlg, state in instanceItems if isinstance(dlg, cls)
		)
		firstMatchingInstance, state = next(instancesOfSameClass, (None, None))
		multiInstanceAllowed = kwargs.get('multiInstanceAllowed', False)
		if log.isEnabledFor(log.DEBUG):
			instancesState = dict(RefocusableMixin._instances)
			log.debug(
				"Creating new revocusable dialog (multiInstanceAllowed:{}). "
				"State of _instances {!r}".format(multiInstanceAllowed, instancesState)
			)
		if state is cls.DialogState.CREATED and not multiInstanceAllowed:
			raise RefocusableMixin.MultiInstanceErrorWithDialog(
				firstMatchingInstance,
				"Only one instance of RefocusableMixin can exist at a time",
			)
		if state is cls.DialogState.DESTROYED and not multiInstanceAllowed:
			# the dialog has been destroyed by wx, but the instance is still available. This indicates there is something
			# keeping it alive.
			log.error("Opening new refocusable dialog while instance still exists: {!r}".format(firstMatchingInstance))
		obj = super(RefocusableMixin, cls).__new__(cls, *args, **kwargs)
		RefocusableMixin._instances[obj] = cls.DialogState.CREATED
		return obj

	def _setInstanceDestroyedState(self):
		# prevent race condition with object deletion
		# prevent deletion of the object while we work on it.
		nonWeak: typing.Dict[RefocusableMixin, RefocusableMixin.DialogState] = dict(RefocusableMixin._instances)

		if (
			self in RefocusableMixin._instances
			# Because destroy handlers are use evt.skip, _setInstanceDestroyedState may be called many times
			# prevent noisy logging.
			and self.DialogState.DESTROYED != RefocusableMixin._instances[self]
		):
			if log.isEnabledFor(log.DEBUG):
				instanceStatesGen = (
					f"{instance.title} - {state.name}"
					for instance, state in nonWeak.items()
				)
				instancesList = list(instanceStatesGen)
				log.debug(
					f"Setting state to destroyed for instance: {self.title} - {self.__class__.__qualname__} - {self}\n"
					f"Current _instances {instancesList}"
				)
			RefocusableMixin._instances[self] = self.DialogState.DESTROYED



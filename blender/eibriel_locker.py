# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os
import bpy
import uuid
import atexit

from bpy.app.handlers import persistent

bl_info = {
    "name": "eLocker",
    "author": "Eibriel",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "Topbar",
    "description": "Lock open blender files",
    "warning": "",
    "wiki_url": "https://github.com/Eibriel/scripts/wiki",
    "tracker_url": "https://github.com/Eibriel/scripts/issues",
    "category": "Eibriel"}


def get_lockpath(filepath):
    return "{}.lock".format(filepath)


def lockunlock(action):
    # If is not saved then return
    if bpy.data.filepath == "":
        return

    new_path = get_lockpath(bpy.data.filepath)

    if action == "LOCK":
        if not os.path.exists(new_path):
            new_lock = open(new_path, 'w')
            new_lock.write(get_uuid())
            new_lock.close()
    elif action == "UNLOCK":
        new_lock = open(new_path, 'r')
        luuid = new_lock.readlines()
        if luuid[0] == get_uuid():
            os.remove(new_path)


@persistent
def load_post_handler(dummy):
    lockunlock("LOCK")


@persistent
def update_handler(dummy):
    lockunlock("LOCK")


@persistent
def load_pre_handler(dummy):
    lockunlock("UNLOCK")


def exit_handler(name, adjective):
    lockunlock("UNLOCK")


def get_uuid():
    pid = os.getpid()
    return "{}-{}".format(pid, hex(uuid.getnode()))


def check_locked():
    unlock = bpy.data.filepath
    if unlock == "":
        return False
    new_path = get_lockpath(unlock)
    if not os.path.exists(new_path):
        return False
    new_lock = open(new_path, 'r')
    luuid = new_lock.readlines()
    return luuid[0] != get_uuid()


def lock_label(self, context):
    if check_locked():
        self.layout.label(text="Locked! Warning, someone else is using this file right now!", icon="ERROR")
        for window in bpy.context.window_manager.windows:
            window.cursor_set("WAIT")


def register():
    bpy.types.TOPBAR_MT_editor_menus.prepend(lock_label)
    bpy.app.handlers.load_post.append(load_post_handler)
    bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.depsgraph_update_post.append(update_handler)

    atexit.register(exit_handler, None, None)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(lock_label)
    bpy.app.handlers.load_post.remove(load_post_handler)
    bpy.app.handlers.load_pre.remove(load_pre_handler)
    bpy.app.handlers.depsgraph_update_post.remove(update_handler)

    atexit.unregister(exit_handler)

if __name__ == "__main__":
    register()

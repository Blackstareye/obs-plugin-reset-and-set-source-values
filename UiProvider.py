# import obspython as obs
# from pathlib import Path
# # from enum import Enum

# # class PropertyKeys(Enum):
# #     SOURCE_NAME = "source_name"
# #     REFRESH_LIST = "refreshbutton"
# #     PATH_TO_SETTING_FILE = "path_to_setting_file"
# #     FILE_CONTENT_TXT = "fileInfo"


# class UiProvider:


#     # @classmethod
#     # def updateFileContent(settings):
#     #     file_path = obs.obs_data_get_string(settings, PropertyKeys.PATH_TO_SETTING_FILE);
#     #     contents = Path(file_path).read_text()
#     #     # TODO load file from path
#     #     obs.obs_data_set_string(settings, PropertyKeys.FILE_CONTENT_TXT, contents);
#     #     # TODO on signal remove hook

#     @classmethod
#     def build():
#         props = obs.obs_properties_create()
#         #obs.obs_properties_add_text(props, "source_name", "Source name", obs.OBS_TEXT_DEFAULT)
#         # Drop-down list of sources
#         list_property = obs.obs_properties_add_list(props, "source_name", "Source name",
#                     obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
#         # Button to refresh the drop-down list
#         obs.obs_properties_add_button(props, "button", "Refresh list of sources",
#             lambda props,prop: True if UiProvider.fillSourceList(list_property) else True)
#         UiProvider.fillSourceList(list_property)

#         p = Path(__file__).absolute()  # current script path
#         pstr : str  = p.parent.as_posix()
#         path = obs.obs_properties_add_path(props, "path_to_setting_file", "Path to the setting file", obs.OBS_PATH_FILE, "json", pstr )
#         # TODO modified hook
#         obs.obs_properties_add_text(props, "fileInfo", "Displays the File Content", obs.OBS_TEXT_INFO | obs.OBS_TEXT_MULTILINE)

#     #     # props = obs.obs_properties_create()
#     #     # #obs.obs_properties_add_text(props, "source_name", "Source name", obs.OBS_TEXT_DEFAULT)
#     #     # # Drop-down list of sources
#     #     # list_property = obs.obs_properties_add_list(props, PropertyKeys.SOURCE_NAME, "Source name",
#     #     #             obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
#     #     # # Button to refresh the drop-down list
#     #     # obs.obs_properties_add_button(props, PropertyKeys.REFRESH_LIST, "Refresh list of sources",
#     #     #     lambda props,prop: True if UiProvider.fillSourceList(list_property) else True)
#     #     # UiProvider.fillSourceList(list_property)

#     #     # p = Path(__file__).absolute()  # current script path
#     #     # pstr : str  = p.parent.as_posix()
#     #     # path = obs.obs_properties_add_path(props, PropertyKeys.PATH_TO_SETTING_FILE, "Path to the setting file", obs.OBS_PATH_FILE, "json", pstr )
#     #     # # TODO modified hook
#     #     # obs.obs_properties_add_text(props, PropertyKeys.FILE_CONTENT_TXT, "Displays the File Content", obs.OBS_TEXT_INFO | obs.OBS_TEXT_MULTILINE)
#         return props

#     @classmethod
#     def fillSourceList(list_property):
#         # Fills the given list property object with the names of all sources plus an empty one
#         sources = obs.obs_enum_sources()
#         obs.obs_property_list_clear(list_property)
#         obs.obs_property_list_add_string(list_property, "", "")
#         for source in sources:
#             name = obs.obs_source_get_name(source)
#             obs.obs_property_list_add_string(list_property, name, name)
#         obs.source_list_release(sources)
import obspython as obs # type: ignore
import json
from pathlib import Path


from enum import Enum

FILERCLASS=obs.OBS_SOURCE_VIDEO
# log = obs.blog
DEBUG = True
USE_OBS_LOGS=False
#FILERCLASS=obs.OBS_SOURCE_AUDIO

      

class PropertyKeys(Enum):
    LISTBOX_SOURCE_NAME = "source_name"
    BT_REFRESH_LIST = "refreshbutton"
    PATH_PATH_TO_SETTING_FILE = "path_to_setting_file"
    TXT_FILE_CONTENT = "fileInfo"
    BT_RESET_SETTINGS = "reset_settings"
    BT_PRINT_SETTINGS = "print_settings"

class DataObject(object):
    source_name =""
    file_name = ""

    def __init__(self, **kwargs):
        #print(kwargs)
        for key in kwargs:
            if hasattr(self, key):
              log(f"Set: {key}:{kwargs[key]}")
              setattr(self, key, kwargs[key])
            else:
              log("Key is not in DataObject. Please fix it. {key}:{kwargs[key]}", throw_exception=True)
    
    # def update(self,*data):
    #    for dictionary in data:
    #         for key in dictionary:
    #             if hasattr(self, key):
    #               setattr(self, key, dictionary[key])
                
    def printObject(self):
      print(f"Object: s:{self.source_name} p:{self.file_name}")

# =================== script ======================

settinginstance = None
dataObject = None
# Called after change of settings including once after script load

def prepare(settings):
   global settinginstance;
   global dataObject;
   settinginstance = settings
   dataObject = DataObject(**toObject(settings))

# TODO on modification or something hook
def script_update(settings):
   prepare(settings)

# Called to set default values of data settings
def script_defaults(settings):
    obs.obs_data_set_default_string(settings, PropertyKeys.LISTBOX_SOURCE_NAME.value, "")
    obs.obs_data_set_default_string(settings, PropertyKeys.PATH_PATH_TO_SETTING_FILE.value, "")
    obs.obs_data_set_default_string(settings, PropertyKeys.TXT_FILE_CONTENT.value, "File will be displayed here.")

# Description displayed in the Scripts dialog window
def script_description():
  return """<center><h2>OBS Camera Reset Button</h2></center>
            <p> Reset the Camera and trigger two commands. Go to <em>Settings
            </em> then <em>Hotkeys</em> to select the key combination.</p><p>Check the <a href=
            "https://github.com/obsproject/obs-studio/wiki/Scripting-Tutorial-Source-Shake.md">
            Source Shake Scripting Tutorial</a> on the OBS Wiki for more information.</p>"""

def script_tick(seconds):
    pass

# Called at script unload
def script_unload():
  pass

# Called before data settings are saved
def script_save(settings):
  pass

# Identifier of the hotkey set by OBS
hotkey_id = obs.OBS_INVALID_HOTKEY_ID
# Callback for the hotkey
def on_shake_hotkey(pressed):
  pass

# Called at script load
def script_load(settings):
    prepare(settings)


def loadSettings(sourcename, reset: bool=True):
  # global dataObject; # not necessary cause object is only read
  # source related entries
  source = obs.obs_get_source_by_name(sourcename)
  settings = obs.obs_source_get_settings(source)

  if reset:
    obs.obs_soure_reset_settings(settings);   
  #p = "/projects/tmp_dev/obs-plugin/python/data.json" #TODO echter pfad noch obs.obs_data_get_string(settings, PropertyKeys.PATH_TO_SETTING_FILE.value);
  dataObject.printObject()
  p = dataObject.file_name
  data = obs.obs_data_create_from_json_file_safe(p, Path(p).joinpath("backup.json").as_posix());
  log(f"path: {p}")
  log(f"data {obs.obs_data_get_json(data)}")
  if data:
    jdata = json.loads(obs.obs_data_get_json(data))
  
  jsettings = json.loads(obs.obs_data_get_json(settings))
  log(f"settings {jsettings}")

  for nk, nv in jdata.items():
        if nk in jsettings:
            log(f"New Value ${nk} with {nv}", force_print=True)
            ObsDataUtility.set_value(settings, nk, nv);
            #obs.obs_data_set_bool(settings, nk, nv) #TODO entscheiden wann bool wann string
  obs.obs_source_update(source, settings)

  obs.obs_data_release(data)
  obs.obs_data_release(settings)
  obs.obs_source_release(source)

#   print(obs.obs_data_get_json(settings))
#   print("---------- new_data ----------")
#   print(obs.obs_data_get_json(data))
#   print(obs.obs_data_get_json(data))

#   print(data)
#   if p:
#     data = json.load(p)
#   for k,d in data:
#      if 
#      obs.obs_data_set_string(settings, k, d);
#apply
  



# TODO on signal remove hook

# obs_data_create_from_json_file_safe
# https://docs.obsproject.com/reference-settings#c.obs_data_create_from_json


# Called to display the properties GUI
def script_properties():
  props = obs.obs_properties_create()
  # Drop-down list of sources
  PropertyUtils.addSourceListAndButton(props)
  PropertyUtils.addFilePath(props)
  PropertyUtils.resetSettings(props, lambda : loadSettings(PropertyUtils.getSource(),  False))
  PropertyUtils.printSettings(props, lambda: print_settings(PropertyUtils.getSource()))
  PropertyUtils.addFileContent(props)
  return props



def print_settings(source):
    source = obs.obs_get_source_by_name(source)
    settings = obs.obs_source_get_settings(source)
    log("[---------- settings ----------", force_print=True)
    log(obs.obs_data_get_json_pretty(settings), force_print=True)
    obs.obs_data_release(settings)
    obs.obs_source_release(source)


# ===================== Helper


class PropertyUtils:
   
    @classmethod
    def addFilePath(cls,props):
        p = Path(__file__).absolute()  # current script path
        pstr : str  = p.parent.as_posix()
        path = obs.obs_properties_add_path(props, PropertyKeys.PATH_PATH_TO_SETTING_FILE.value, "Path to the setting file", obs.OBS_PATH_FILE, "json", pstr )
        # TODO modified hook
        
    @classmethod
    def addFileContent(cls, props):
       obs.obs_properties_add_text(props, PropertyKeys.TXT_FILE_CONTENT.value, "Displays the File Content", obs.OBS_TEXT_INFO | obs.OBS_TEXT_MULTILINE)
    
    @classmethod
    def resetSettings(cls, props, callback):
       obs.obs_properties_add_button(props, PropertyKeys.BT_RESET_SETTINGS.value, "Reset and set Defaults",
        lambda props,prop: True if callback() else True)
    @classmethod
    def printSettings(cls, props, callback):
       obs.obs_properties_add_button(props, PropertyKeys.BT_PRINT_SETTINGS.value, "Print Settings",
        lambda props,prop: True if callback() else True)

    @classmethod
    def addSourceListAndButton(cls, props):
        list_property = obs.obs_properties_add_list(props, PropertyKeys.LISTBOX_SOURCE_NAME.value, "Source name",
              obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
        
        # Button to refresh the drop-down list
        obs.obs_properties_add_button(props, PropertyKeys.BT_REFRESH_LIST.value, "Refresh list of sources",
        lambda props,prop: True if cls.fillSourceList(list_property, FILERCLASS) else True)
        cls.fillSourceList(list_property, FILERCLASS)

    @classmethod
    def loadFileContentInField(cls, settings):
        file_path = obs.obs_data_get_string(settings, PropertyKeys.PATH_PATH_TO_SETTING_FILE.value);
        if file_path:
            contents = Path(file_path).read_text()
            # TODO load file from path
            obs.obs_data_set_string(settings, PropertyKeys.TXT_FILE_CONTENT.value, contents);
    
    @classmethod
    def fillSourceList(cls,list_property, filters : int=None):
        # Fills the given list property object with the names of all sources plus an empty one
        sources = obs.obs_enum_sources()
        obs.obs_property_list_clear(list_property)
        obs.obs_property_list_add_string(list_property, "", "")
        for source in sources:
            #flags = obs.obs_source_get_output_flags()
            if filters:
              flags = obs.obs_source_get_output_flags(source)
              if flags & filters == filters:
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(list_property, name, name)
            else:
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(list_property, name, name)
        obs.source_list_release(sources)
       
    @classmethod
    def getSource(cls):
       global settinginstance;
       l = obs.obs_data_get_string(settinginstance, PropertyKeys.LISTBOX_SOURCE_NAME.value);
       log(f"source is {l}")
       return l
    
class ObsDataUtility:
   @classmethod
   def set_value(cls, settings, name, value):
      # Versuche, in einen Integer zu konvertieren
      try:
          log(f"trying int parsing for {value}")
          v = int(value)
          obs.obs_data_set_int(settings, name, v);
          return
      except ValueError:
          pass
      
      # Versuche, in einen Float zu konvertieren
      try:
          log(f"trying double parsing for {value}")
          f =  float(value)
          obs.obs_data_set_double(settings, name, f);
          return
      except ValueError:
          pass
      
      # Versuche, in einen Boolean zu konvertieren
      log(f"trying bool parsing for {value}")
      if value.lower() in ('true', '1', 'yes'):
          obs.obs_data_set_double(settings, name, True);
          return
      elif value.lower() in ('false', '0', 'no'):
          obs.obs_data_set_double(settings, name, False);
          return
      log(f"trying string parsing for {value}")
      obs.obs_data_set_string(settings, name, value);
      



def toObject(settings):
   if settings:
      filename = obs.obs_data_get_string(settings, PropertyKeys.PATH_PATH_TO_SETTING_FILE.value);
      sourcename = obs.obs_data_get_string(settings, PropertyKeys.LISTBOX_SOURCE_NAME.value);
      log(f"s:{sourcename} p:{filename}")
      return {"source_name": sourcename, "file_name": filename}



def log(txt, throw_exception : bool=False,level=None, force_print=False):
   if USE_OBS_LOGS:
      level = level if level else obs.LOG_DEBUG if DEBUG else obs.LOG_INFO;
      obs.blog(level, txt)
   else:
      if DEBUG or force_print:
        print(txt)
   if throw_exception:
      raise Exception(f">>LOOK LOG \n {txt}")
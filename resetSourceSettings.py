import obspython as obs # type: ignore
import json
from pathlib import Path


from enum import Enum

# change if you filter Video or Audio Sources
FILERCLASS=obs.OBS_SOURCE_VIDEO
# change if the resource should be reset before overwriting
RESET=True

# Debug enables logging
DEBUG = True
USE_OBS_LOGS=False

      

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
   PropertyUtils.loadFileContentInField(settings)

# Called to set default values of data settings
def script_defaults(settings):
    obs.obs_data_set_default_string(settings, PropertyKeys.LISTBOX_SOURCE_NAME.value, "")
    obs.obs_data_set_default_string(settings, PropertyKeys.PATH_PATH_TO_SETTING_FILE.value, "")
    obs.obs_data_set_default_string(settings, PropertyKeys.TXT_FILE_CONTENT.value, "File will be displayed here.")

# Description displayed in the Scripts dialog window
def script_description():
  return """<center><h2>OBS source setting reset and set values</h2></center>
            <p> Reset the source and load the values from the chosen json file into the source object. Go to <em>Settings
            </em> then <em>Hotkeys</em> to select the key combination. created by <a href=https://github.com/Blackstareye>Blackeye</a></p>
            If you like this Script you can support me via <a href=https://ko-fi.com/black_eye>Kofi</a>
            """

# Global animation activity flag
is_active = False
# Called every frame
def script_tick(seconds):
  if is_active:
    loadSettings(dataObject.source_name)

# Called at script unload
def script_unload():
  pass

# Called before data settings are saved
def script_save(settings):
  obs.obs_save_sources()

# Identifier of the hotkey set by OBS
hotkey_id = obs.OBS_INVALID_HOTKEY_ID
# Callback for the hotkey
def on_hotkey_pressed(pressed):
  global is_active
  is_active = pressed

def loadHotkeys():
  global hotkey_id
  global settinginstance
  hotkey_id = obs.obs_hotkey_register_frontend(script_path(), "Reset and Update Settings", on_hotkey_pressed)
  hotkey_save_array = obs.obs_data_get_array(settinginstance, "reset_update_hotkey")
  obs.obs_hotkey_load(hotkey_id, hotkey_save_array)
  obs.obs_data_array_release(hotkey_save_array)

# Called at script load
def script_load(settings):
    prepare(settings)
    loadHotkeys()


def loadSettings(sourcename, reset: bool=True):
  # global dataObject; # not necessary cause object is only read
  # source related entries
  source = obs.obs_get_source_by_name(sourcename)
  settings = obs.obs_source_get_settings(source)

  if reset:
    obs.obs_source_reset_settings(source,settings);   
    # obs.obs_source_media_start(source)
  dataObject.printObject()

  p = dataObject.file_name
  data = obs.obs_data_create_from_json_file_safe(p, Path(p).joinpath("backup.json").as_posix());
  log(f"path: {p}")
  log(f"data {obs.obs_data_get_json(data)}")
  if data:
    jdata = json.loads(obs.obs_data_get_json(data))
    log(f"jdata {jdata}")
  
  jsettings = json.loads(obs.obs_data_get_json(settings))
  log(f"settings {jsettings}")

  for nk, nv in jdata.items():
        #if nk in jsettings:
            log(f"New Value ${nk} with {nv}", force_print=True)
            ObsDataUtility.set_value(settings, nk, nv);
  obs.obs_source_update(source, settings)
  obs.obs_save_sources()
  # release
  obs.obs_data_release(data)
  obs.obs_data_release(settings)
  obs.obs_source_release(source)

# Called to display the properties GUI
def script_properties():
  props = obs.obs_properties_create()
  # Drop-down list of sources
  PropertyUtils.addSourceListAndButton(props)
  PropertyUtils.addFilePath(props)
  PropertyUtils.printSourceSettings(props, lambda: print_settings(PropertyUtils.getSource()))
  PropertyUtils.updateSettings(props, lambda : loadSettings(PropertyUtils.getSource()))
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
        path = obs.obs_properties_add_path(props, PropertyKeys.PATH_PATH_TO_SETTING_FILE.value, "Setting file:", obs.OBS_PATH_FILE, "json", pstr )
        # TODO modified hook
        
    @classmethod
    def addFileContent(cls, props):
       obs.obs_properties_add_text(props, PropertyKeys.TXT_FILE_CONTENT.value, "File Content:", obs.OBS_TEXT_INFO | obs.OBS_TEXT_MULTILINE)
    
    @classmethod
    def updateSettings(cls, props, callback):
       obs.obs_properties_add_button(props, PropertyKeys.BT_RESET_SETTINGS.value, "Reset source settings and update values",
        lambda props,prop: True if callback() else True)
    @classmethod
    def printSourceSettings(cls, props, callback):
       obs.obs_properties_add_button(props, PropertyKeys.BT_PRINT_SETTINGS.value, "Print source settings",
        lambda props,prop: True if callback() else True)

    @classmethod
    def addSourceListAndButton(cls, props):
        list_property = obs.obs_properties_add_list(props, PropertyKeys.LISTBOX_SOURCE_NAME.value, "Source name to update",
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
      
            # Versuche, in einen Boolean zu konvertieren
      log(f"trying bool parsing for {value}")
      #if value.lower() in ('true', '1', 'yes'):
      if type(value) is bool:
          #obs.obs_data_set_bool(settings, name, True if value in ('true', '1', 'yes', 1) else False);
          obs.obs_data_set_bool(settings, name, value);
          return
      # elif value.lower() in ('false', '0', 'no'):
      #     obs.obs_data_set_double(settings, name, False);
      
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
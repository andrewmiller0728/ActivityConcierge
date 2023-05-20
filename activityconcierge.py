# activityconcierge.py


''' ACTIVITY CONCIERGE
        This is the main module for the Activity Concierge application.
        The Activity Concierge is a tool that helps users manage their activities.
        Functions include:
            - help menu
            - add an activity
            - remove an activity
            - edit an activity
            - list all activities
            - score an activity
            - backup the database
        Andrew Miller, 2023
'''


''' TODO                                                                                                             '''
#   - command class
#   - gpt integration:
#     - write activity description
#     - write activity tags
#     - generate new activity with description and tags
#   - restore function


''' IMPORTS                                                                                                          '''

import os
import datetime
import sys
from prettytable import PrettyTable


''' CONSTANTS                                                                                                        '''

ACTC_DATA = "./activities.dat"
ACTC_LOG = "./activities.log"
ACTC_BACKUP_DIR = "./backups"

ACTC_LOG_FORMAT = "%Y-%m-%d %H:%M:%S"
ACTC_LOG_HEADER = "[[[ ACTIVITY CONCIERGE LOG ]]]\n\n"
ACTC_BACKUP_FORMAT = "%Y-%m-%d_%H-%M-%S"


''' CLASSES                                                                                                          '''

''' Tag                                                                                                              '''
#       This class represents a tag that can be associate with an activity.
#       Tags are used to categorize activities.
#       Tag attributes:
#         - name: a unique, non-empty, case-specific string of alphanumeric characters
class Tag:

    tags = list()

    def __init__(self, name:str) -> None:
        if name is None:
            raise ValueError("Tag name cannot be None.")
        elif len(name) == 0:
            raise ValueError("Tag name cannot be empty.")
        elif not name.isalnum():
            raise ValueError("Tag name must be alphanumeric.")
        else:
            self.name = name.upper()
            self.activities = list()
            if self.name in Tag.tags:
                raise ValueError("Tag name must be unique.")
            else:
                Tag.tags.append(self.name)
        pass

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Tag) and self.name == o.name

    def __str__(self) -> str:
        return self.name

# end Tag class


''' Activity                                                                                                         '''
#       This class represents an activity that the user can do.
#       Activity attributes:
#         - name
#         - description
#         - list of Tag objects
#         - ease score (must be an integer between 0 and 10, inclusive)
#         - reward score (must be an integer between 0 and 10, inclusive)
class Activity:

    def __init__(self, name: str, description: str, tags: list, ease: int, reward: int) -> None:
        if ease not in range(0, 11):
            raise ValueError("Ease score must be an integer between 0 and 10, inclusive.")
        if reward not in range(0, 11):
            raise ValueError("Reward score must be an integer between 0 and 10, inclusive.")
        self.name = name.upper()
        self.description = description
        self.tags = tags
        self.ease = ease
        self.reward = reward
        pass

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Activity):
            return self.name == o.name
        else:
            return False
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        if len(self.tags) == 0:
            return f"{self.name}:{self.description}:[]:({self.ease}:{self.reward})"
        else:
            tags_str = self.get_tags_str()
            return f"{self.name}:{self.description}:[{tags_str}]:({self.ease}:{self.reward})"
    
    def attach_tag(self, tag: Tag) -> bool:
        if tag not in self.tags:
            self.tags.append(tag)
            tag.activities.append(self)
            return True
        else:
            return False

    def get_tags_str(self) -> str:
        tags_str = ""
        for tag in self.tags:
            tags_str += f"{tag},"
        tags_str = tags_str[:-1]
        return tags_str

# end Activity class


''' FUNCTIONS                                                                                                        '''

''' __get_help_menu__                                                                                                '''
#       This function returns a verbose help menu as a string.
#       The help menu first list the available commands and required/optional arguments, then describes each command 
#       in detail. Finally, the help menu describes an Activity object and its attributes.
#       Logging is not necessary for this function.
def __get_help_menu__() -> str:
    help_str =  '\n[ Activity Concierge Manual ]\n\n\n'
    help_str += 'Syntax:\n\t- <command> <required arguments> [optional arguments]\n\n\n'
    help_str += 'Activity Object:\n\n'
    help_str += '\t- <name>\t\tthe name of the activity\n'
    help_str += '\t- [description] \ta description of the activity\n'
    help_str += '\t- [tags] \t\ta list of tags for the activity\n'
    help_str += '\t- [ease] \t\tthe ease score of the activity [1,10]\n'
    help_str += '\t- [reward] \t\tthe reward score of the activity [1,10]\n\n\n'
    help_str += 'Command Usage:\n\n'
    help_str += '\t- help\n'
    help_str += '\t- list\n'
    help_str += '\t- add <name> [description] [tags] [ease] [reward]\n'
    help_str += '\t- remove <name>\n'
    help_str += '\t- edit <name> [description] [tags] [ease] [reward]\n'
    help_str += '\t- score <name>\n'
    help_str += '\t- backup\n\n\n'
    help_str += 'Command Descriptions:\n\n'
    help_str += '\t- help \t\t\tdisplays what you\'re currently reading\n'
    help_str += '\t- list \t\t\tlists all activities currently in the database\n'
    help_str += '\t- add \t\t\tadds a new activity to the database\n'
    help_str += '\t\t\t\t\t- <name> \t\t\tthe name of the activity\n'
    help_str += '\t\t\t\t\t- [description] \t\ta description of the activity\n'
    help_str += '\t\t\t\t\t- [tags] \t\t\ta list of tags for the activity\n'
    help_str += '\t\t\t\t\t- [ease] \t\t\tthe ease score of the activity [1,10]\n'
    help_str += '\t\t\t\t\t- [reward] \t\t\tthe reward score of the activity [1,10]\n'
    help_str += '\t- remove \t\tremoves an activity from the database\n'
    help_str += '\t\t\t\t\t- <name> \t\t\tthe name of the activity\n'
    help_str += '\t- edit \t\t\tedits the attributes of an activity in the database\n'
    help_str += '\t\t\t\t\t- <name> \t\t\tthe name of the activity to be edited\n'
    help_str += '\t\t\t\t\t- [description] \t\ta new description of the activity\n'
    help_str += '\t\t\t\t\t- [tags] \t\t\ta new list of tags for the activity\n'
    help_str += '\t\t\t\t\t- [ease] \t\t\ta new ease score for the activity [1,10]\n'
    help_str += '\t\t\t\t\t- [reward] \t\t\ta new reward score for the activity [1,10]\n'
    help_str += '\t- score \t\tdisplays the composite score of an activity\n'
    help_str += '\t\t\t\t\t- <name> \t\t\tthe name of the activity\n'
    help_str += '\t- backup \t\tcreates a timestamped backup of the data file\n\n\n'
    return help_str

''' __log_msg__                                                                                                      '''
#       This function formats a message for logging and appends it to the log file.
#       Log messages begin with a timestamp and end with a newline.
#       It returns the formatted log message.
def __log_msg__(message: str, console_print:bool=False) -> str:
    timestamp = datetime.datetime.now().strftime(ACTC_LOG_FORMAT)
    log_entry = f"[{timestamp}] \t{message}\n"
    if console_print:
        print(log_entry, end="")
    if not os.path.exists(ACTC_LOG):            # if log file does not exist, create it
        with open(ACTC_LOG, "w") as log_file:
            log_file.write(ACTC_LOG_HEADER)
            log_file.write(log_entry)
    else:                                       # otherwise, append to it
        with open(ACTC_LOG, "a") as log_file:
            log_file.write(log_entry)
    return log_entry

''' __get_activity__                                                                                                 '''
#       This function returns an activity object from the database given the activity name.
#       If the activity is not found, it raises an exception.
def get_activity(activities:list, activity_name: str) -> Activity:
    for activity in activities:
        if activity.name == activity_name.upper():
            return activity
    return None

''' backup_data                                                                                                      '''
#       This function creates a timestamped backup of the data file and saves it to the backups folder.
#       The backup file is saved as <activities_yyyy-mm-dd_hh-mm-ss.dat>.
#       It returns the path of the backup file.
def backup_data() -> str:
    bfile_name = f"activities_{datetime.datetime.now().strftime(ACTC_BACKUP_FORMAT)}.dat"
    bfile_path = os.path.join(ACTC_BACKUP_DIR, bfile_name)
    try:
        with open(ACTC_DATA, "r") as data_file:
            with open(bfile_path, "w") as backup_file:
                for line in data_file:
                    backup_file.write(line)
    except FileNotFoundError:
        __log_msg__(f"Could not find Activities data file \'{ACTC_DATA}\'")
    except Exception as e:
        __log_msg__(f"Error backing up Activities data file \'{ACTC_DATA}\': {e}")
    finally:
        return bfile_path

''' load_activities                                                                                                  '''
#       This function loads the activities from the data file.
#       It takes the path to the data file as an argument.
#       The activity data file is formatted as follows:
#           <name>:<description>:[<tags>]:(<ease>:<reward>)
#       It returns a list of Activity objects.
def load_activities(activity_data:str) -> list:
    __log_msg__(f"Loading activities from \'{activity_data}\'...")
    activities = []
    try:
        with open(activity_data, "r") as dfile:
            for line in dfile:
                name, description, tags, ease, reward = line.split(":")
                tags = tags[1:-1].split(", ")
                ease = int(ease[1:])
                reward = int(reward[:-2])
                activities.append(Activity(name, description, tags, ease, reward))
                __log_msg__(f"\tLoaded activity \'{name}\'.")
    except FileNotFoundError:
        __log_msg__(f"Could not find Activities data file \'{activity_data}\'", True)
    except Exception as e:
        __log_msg__(f"Error loading Activities data file \'{activity_data}\': {e}", True)
    finally:
        __log_msg__(f"Loaded {len(activities)} activities from \'{activity_data}\'.", True)
        return activities

''' save_activities                                                                                                  '''
#       This function saves the activities to the data file.
#       It returns True if the save was successful, False otherwise.
def save_activities(activities:list, activity_data:str) -> bool:
    __log_msg__(f"Saving activities to \'{activity_data}\'...")
    tfile = activity_data + ".tmp"
    __log_msg__(f"\tWriting to temp file \'{tfile}\'...")
    try:
        with open(tfile, "w") as temp_file:
            for activity in activities:
                temp_file.write(repr(activity) + "\n")
                __log_msg__(f"\t\tWrote activity \'{activity.name}\' to temp file as \'{repr(activity)}\'.")
    except Exception as e:
        __log_msg__(f"Error writing to temp file \'{tfile}\': {e}", True)
        return False
    finally:
        temp_file.close()
    __log_msg__(f"\tOverwriting \'{activity_data}\' with temp file \'{tfile}\'...")
    try:
        os.replace(tfile, activity_data)
    except Exception as e:
        __log_msg__(f"Error overwriting data file \'{activity_data}\' with temp file \'{tfile}\': {e}", True)
        return False
    finally:
        temp_file.close()
        if os.path.exists(tfile):
            __log_msg__(f"\tRemoving temp file \'{tfile}\'...")
            os.remove(tfile)
    __log_msg__(f"Saved {len(activities)} activities to \'{activity_data}\'.", True)
    return True

''' add_activity                                                                                                     '''
#       This function adds an activity to a list of activities if the activity is not already present.
#       The user can optionally specify description, tags, ease, and reward. If unspecified, default values are used.
#       It returns True if the activity was added, False otherwise.
def add_activity(activities:list, name: str, description: str = "", tags: list = [], ease: int = 0, reward: int = 0) -> bool:
    __log_msg__(f"Adding activity \'{name}\'...")
    if get_activity(activities, name):
        __log_msg__(f"\tActivity \'{name}\' already exists.", True)
        return False
    else:
        activities.append(Activity(name, description, tags, ease, reward))
        __log_msg__(f"\tAdded activity \'{name}\'.", True)
        return True

''' remove_activity                                                                                                  '''
#       This function removes an activity from the list of activities if it is present.
#       It returns True if the activity was removed, False otherwise.
def remove_activity(activities:list, name: str) -> bool:
    __log_msg__(f"Removing activity \'{name}\'...")
    activity = get_activity(activities, name)
    if activity is not None:
        activities.remove(activity)
        __log_msg__(f"\tRemoved activity \'{name}\'.", True)
        return True
    else:
        __log_msg__(f"\tActivity \'{name}\' not found.", True)
        return False

''' edit_activity                                                                                                    '''
#       This function edits an activity in the list of activities if it is present.
#       It prompts the user for the new values of the activity's attributes one at a time.
#       It returns True if the activity was present & edited, False otherwise.
def edit_activity(activities:list, name: str) -> bool:
    activity = get_activity(activities, name)
    if activity is not None:
        __log_msg__(f"User editing activity \'{activity.name}\'...")
        print('Enter new values for each attribute. Press Enter to keep the current value.')
        activity.description = input(f"Description [{activity.description}]: ").strip().strip('\'\"') or activity.description
        activity.tags = input(f"Tags [{activity.tags}]: ").strip().strip('\'\"').split(',') or activity.tags
        activity.ease = input(f"Ease [{activity.ease}]: ") or activity.ease
        activity.reward = input(f"Reward [{activity.reward}]: ") or activity.reward
        __log_msg__(f"User edited activity \'{activity.name}\'.")
        return True
    else:
        return False

''' score_activity                                                                                                   '''
#       This function returns a composite score for an activity based on its ease and reward scores.
#       Currently, the composite score is calulated as the sum of the reward score and the ease score.
#       TODO: refine scoring algorithm
def score_activity(activity: Activity) -> float:
    score = activity.reward + activity.ease
    __log_msg__(f"Scored activity \'{activity.name}\' with ease {activity.ease} and reward {activity.reward} as {score}.")
    return score


''' MAIN                                                                                                             '''
#       This function runs activty commands based on command line arguments and saves before exiting.
#       If no args are provided, it prints a help message.
#       If args are provided, it runs the command specified by the first arg, passing the remaining args to the command.
#       The remaining args required differ for each command, and are documented in the help message.
#       The activities are always loaded from the "activities.dat" file, and saved to the same file before exiting.
def main() -> None:
    __log_msg__('[[[BEGIN PROGRAM]]]')
    __log_msg__('Initializing program...', True)
    activities = load_activities(ACTC_DATA)
    if len(sys.argv) == 1:
        __log_msg__(f"No args provided. Printing help menu...")
        print(f"Usage: {sys.argv[0]} [help | list | add | remove | edit | score | backup]")
    elif sys.argv[1] == "help":
        __log_msg__(f"User requested help menu.")
        print(__get_help_menu__())
    elif sys.argv[1] == "list":
        if len(activities) == 0:
            print('\nNo activities found.\n')
        else:
            print()
            table = PrettyTable(['NAME', 'EASE', 'REWARD', 'SCORE', 'DESCRIPTION', 'TAGS'])
            for activity in activities:
                name = activity.name
                ease = activity.ease
                reward = activity.reward
                score = score_activity(activity)
                description = activity.description
                tags = activity.get_tags_str()
                table.add_row([name, ease, reward, score, description, tags])
            table.align['EASE'] = 'r'
            table.align['REWARD'] = 'r'
            table.align['SCORE'] = 'r'
            print(table.get_string(sortby='SCORE', reversesort=True))
            print()
    elif sys.argv[1] == "add":
        if len(sys.argv) < 3:
            print(f"Usage: {sys.argv[0]} add <activity> [description] [tags] [ease] [reward]")
        else:
            if len(sys.argv) < 7:
                __log_msg__(f"WARNING: Using default values for activity \'{sys.argv[2]}\'", True)
                if len(sys.argv) < 4: 
                    add_activity(activities, sys.argv[2])
                elif len(sys.argv) < 5:
                    add_activity(activities, sys.argv[2], sys.argv[3])
                elif len(sys.argv) < 6:
                    add_activity(activities, sys.argv[2], sys.argv[3], sys.argv[4].split(','))
            else:
                add_activity(activities, sys.argv[2], sys.argv[3], sys.argv[4].split(','), int(sys.argv[5]), int(sys.argv[6]))
    elif sys.argv[1] == "remove":
        if len(sys.argv) < 3:
            print(f"Usage: {sys.argv[0]} remove <activity>")
        else:
            remove_activity(activities, sys.argv[2])
    elif sys.argv[1] == "edit":
        if len(sys.argv) < 3:
            print(f"Usage: {sys.argv[0]} edit <activity>")
        else:
            edit_activity(activities, sys.argv[2])
    elif sys.argv[1] == "score":
        if len(sys.argv) < 3:
            print(f"Usage: {sys.argv[0]} score <activity>")
        else:
            print(score_activity(activities[sys.argv[2]]))
    elif sys.argv[1] == "backup":
        backup_data()
    else:
        print(f"Usage: {sys.argv[0]} [help | list | add | remove | edit | score | backup]")
    save_activities(activities, ACTC_DATA)
    __log_msg__('Exiting program...', True)
    __log_msg__('[[[END PROGRAM]]]')
    return None


''' RUN                                                                                                              '''
#       If this module is run directly as a script, run the main function.
if __name__ == '__main__':
    main()

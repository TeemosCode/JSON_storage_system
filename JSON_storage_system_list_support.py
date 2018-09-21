import json
from collections import OrderedDict


class DataStorage:
    def __init__(self):
        self.data_counter = 0
        self.data_storage = {}
        # If we want to keep the output EXACTLY the SAME as the input string format
        self.string_data_storage = {}

        # support extra type data input storage
        self.support_type_functions = {
            "list": self.search_list,  # type method to handle the particular type input and logic
        }
        # support list type data inputs
        self.support_type_data_storage = {
            "list": {}
        }

        self.command_action = {"add": self.add, "get": self.get, "delete": self.delete, "printout": self.printout}

    def printout(self, data_entry):  # Self Checking Method: Prints out all data in data_storage
        print(self.data_storage)
        print("shit")
        print(self.support_type_data_storage)

    def check_type_support(self, input_data: OrderedDict) -> tuple:
        """
        Check if user input is based on a supported data type.
        If yes, the user input would be in a format of {"type" : "[supported type name]"}.
        :param input_data: user input query dictionary
        :return: tuple with the 0th index being a boolean value indicating if the type is a supported data type, the 1st
        index being the value of the supported data type string name used to pass on to the add, get, delete method
        indicating the matching method for call
        """
        # look for the supported data type input format, and validate if the data type is currently supported in the system or not
        if ("type" in input_data) and (input_data["type"] in self.support_type_functions):
            return True, input_data["type"]
        return False, None

    def add(self, input_data: OrderedDict, input_string_data: str) -> None:
        """
        Takes an string json format input data from the user, turn it into a Ordered Dictionary, and save it
        into the dictionary storage with an unique 'count' to work as the saved data id in the ordered dictionary
        :param input_data: An user input json format data in string type
        :return: None
        """
        # Check if the data type is supported in the system with check_type_support method
        is_supported_type, type_name = self.check_type_support(input_data)
        if is_supported_type:
            # ignore duplicate data
            if input_data in self.support_type_data_storage[type_name].values():
                return
            self.support_type_data_storage[type_name][self.data_counter] = input_data

        else:
            # If added in same data, ignore it
            if input_data in self.data_storage.values():
                return
            # loading user input data as an orderedDictionary
            self.data_storage[self.data_counter] = input_data
        # If we want to keep the output EXACTLY the SAME as the input string format
        self.string_data_storage[self.data_counter] = input_string_data
        self.data_counter += 1  # update the data id in the storage dictionary

    def check_and_find_data(self, input_data: OrderedDict) -> list:
        # Check if the data type is supported in the system with check_type_support method
        is_supported_type, type_name = self.check_type_support(input_data)
        if is_supported_type:
            found_data = self.search(input_data, support_type=type_name)
        else:
            found_data = self.search(input_data)
        return found_data

    def get(self, input_data: OrderedDict) -> None:
        # Check if the data type is supported in the system with check_type_support method
        found_data = self.check_and_find_data(self, input_data)
        # Queried data doesn't exist
        if found_data is None:
            return

        for data in found_data:
            # print(dict(self.data_storage[data]))
            print(self.string_data_storage[data])

    def delete(self, input_data: OrderedDict) -> None:
        # Check if the data type is supported in the system with check_type_support method
        found_data = self.check_and_find_data(self, input_data)
        # Queried data doesn't exist
        if found_data is None:
            return  ## Can modulize this part

        for data in found_data:
            del self.data_storage[data]

    def search_list(self, input_data: OrderedDict) -> list:
        """
        The method used to for the 'list' supported data type to search through both the user input query list data
        and each list data saved in the system. It keeps track of the number of all element's occurrences for both
        user input query data and the list_type data saved within the system. If all elements in the user input queried
        data is in the data within the system and those occurrences are smaller than the occurrences in the data within
        the system, it means that the data within the system matches what the user is querying for. Keeps track of the
        keys of the matched list data within the system and passes the list to the get or delete method for futher actions
        :param input_data:  user input dictionary queried data
        :return: A list of all the keys of the matched list data within the system to keep track of the input order
        """
        matched_list = list()
        query_list_data = input_data["list"]
        query_list_value_map = {}
        for number in query_list_data:
            query_list_value_map[number] = query_list_value_map.get(number, 0) + 1

        for k, data_dict in self.support_type_data_storage["list"].items():
            kth_data_match = True
            list_value_map = {}
            for number in data_dict["list"]:
                list_value_map[number] = list_value_map.get(number, 0) + 1
            for number in query_list_value_map:
                if number not in list_value_map:
                    kth_data_match = False
                    break
                if query_list_value_map[number] > list_value_map[number]:
                    kth_data_match = False
                    break
            if kth_data_match:
                matched_list.append(k)

        return matched_list

    def search(self, input_data: OrderedDict, support_type=None) -> list:
        """
        Used to record the 'keys' (counter) of all the data in the 'general' data_storage system that has all the
        key - value data matching all of the user queried input data. It also validates if the current search is used
        for a supported data type or not and validates the data according to the supported data type.
        :param input_data: The json input of the user query that is now a OrderedDict type
        :param support_type: None for general queries. String support type name for supported data type
        :return: list of keys of the matched data in the storage system
        """
        # If the query is used to query for a particular supported data type, run the 'specific' data type query
        # Otherwise run the 'general' data type query
        if support_type is not None:
            matched_data_key_list = self.support_type_functions[support_type](input_data)
        else:
            matched_data_key_list = list()
            for data_key in self.data_storage:
                # Call on the recursive search to validate if ALL queries are in each stored data
                if self.__recur(input_data, self.data_storage[data_key]):
                    matched_data_key_list.append(data_key)  # Save the keys of the data that matches all queried data
        return matched_data_key_list

    def __recur(self, query_dict, data_storage_dict) -> bool:
        """
        Recursively (There may be a lot of nested json format data) go through both user input queries and each data
        dictionary in the data storage to validate if each data in the data storage consists of all the user input
        queried data. If valid, return True, else returns False
        :param query_dict: The user input query dictionary
        :param data_storage_dict: Each data dictionary in the data storage
        :return: True if all values in the user input query dictionary are in the data storage, else False
        """
        for key in query_dict:
            if key not in data_storage_dict:
                return False
            # if the value is dictionary, it means it is nested, call on the function itself to loop through the nested data
            if isinstance(query_dict[key], dict):
                if not isinstance(data_storage_dict[key], dict):
                    return False
                # returns the validation of all nested data below the current data level
                query_data_in_next_level = self.__recur(query_dict[key], data_storage_dict[key])
                if not query_data_in_next_level:
                    return False
            else:
                if query_dict[key] != data_storage_dict[key]:
                    return False
        return True  # If it did not return False, it means all data queries are this particular data and return True

    def main(self):
        data = ''
        while data is not None:
            try:
                data = input("Json file Input: ")
            except EOFError:
                return
            command, data_entry = data.split(" ", 1)
            ordered_dict_data_entry = OrderedDict(json.loads(data_entry))  # Transform input string data into OrderedDictionary
            #self.command_action[command](ordered_dict_data_entry)
            if command == "add":
                self.add(ordered_dict_data_entry, data_entry)
            elif command == "get":
                self.get(ordered_dict_data_entry)
            elif command == "delete":
                self.delete(ordered_dict_data_entry)

            ###
            elif command == "printout":
                self.printout(ordered_dict_data_entry)



if __name__ == "__main__":
    storage_system = DataStorage()
    storage_system.main()


#  add {"1": "2"}
#  printout {"1": "3"}

#  add {"id" : "4", "city": "san jose", "location" : "west", "info" : "2"}
# add {"id" : "3", "city": "san jose", "location" : {"city" : "san jose", "state" : "ca"}, "info" : "2"}
# add {"id" : "1", "city": "san jose", "location" : {"city" : "san jose", "state" : {"bureau": "spiderman"}}, "info" : "2"}

# add {"id": 1, "last": "Doe", "first": "John", "location": {"city" : "Oakland", "state":"CA","postalCode":"94607"},"active":true}
# add {"id": 2, "last": "Doe", "first": "Jane", "location": {"city" : "San Francisco", "state":"CA","postalCode":"94105"},"active":true}
# add {"id": 3, "last": "Black", "first": "Jim", "location": {"city" : "Spokane", "state":"WA","postalCode":"99207"},"active":true}
# add {"id": 4, "last": "Frost", "first": "Jack", "location": {"city" : "Seattle", "state":"WA","postalCode":"98204"},"active":false}
# get {"location":{"state":"WA"}, "active":true}
# get {"id":1}

# add {"id": "3", "country": "Taiwan", "location": {"city": "Taipei", "state": "CA", "address": {"road": "100", "street": "shit_street"},"yo":"3"}}

# add {"id": "2", "country": "Taiwan", "location": {"city": "san jose", "state": "CA", "address": {"road": "100", "street": "maple"},"yo":"2"}}
# add {"id": "4", "country": "China", "location": {"city": "Taipei", "state": "CA", "address": {"road": "505", "street": "maple"},"yo":"7"}}
# add {"id": "5", "country": "USA", "location": {"city": "san jose", "state": "LA", "address": {"road": "505", "street": "maple"},"yo":"8"}}

#### List supports
# {"type":"list", "list":[1,2,3,4,5]}
# add {"type":"list", "list":[1,2,3,4]}
# add {"type":"list", "list":[2,3,4,5]}
# add {"type":"list", "list":[3,4,5,6]}
# add {"type":"list", "list":[4,5,6,7]}
# add {"type":"list", "list":[5,6,7,8]}
# add {"type":"list", "list":[6,7,8,9]}
# get {"type":"list", "list":[1]}
# get {"type":"list", "list":[3,4]}




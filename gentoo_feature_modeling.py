import vara_feature as vf
import logging as log
import nest_asyncio
nest_asyncio.apply()

from datetime import datetime
from collections import defaultdict



class gentoo_feature_modeling:

    def __init__(self):
        var__now = datetime.now()
        var__nowStr = var__now.strftime("%Y%m%d_%H%M%S")

        log.basicConfig(level=log.DEBUG, filename='gentoo_feature_modeling_'+var__nowStr+'.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
        log.debug("initializing..")

        #initializing all variables
        self.parents = defaultdict(list)
        self.ORgrouping = defaultdict(list)
        self.XORgrouping = defaultdict(list)
        self.MAYgrouping = defaultdict(list)
        self.extConstraints = defaultdict(list)
        self.defaultCounter = 0

        self.useflags = ""
        self.packageName = ""

        self.orCounter = 1
        self.xorCounter = 1
        self.mayCounter = 1
        self.extCounter = 1

        self.feature_builder = vf.feature_model_builder.FeatureModelBuilder()


    ##################### helper functions #####################
    def __create_features(self):
        #create root
        self.feature_builder.make_root(self.packageName)

        #create features of all useflags
        for useflag in self.useflags:
            if useflag.startswith("+") == True: 
                self.feature_builder.make_binaraddFeaturey_feature(useflag[1:], True)
                self.useflags.remove(useflag)
                self.useflags.insert(0, useflag[1:])
            else:
                self.feature_builder.make_binary_feature(useflag, True)

    def __create_constraints(self):
        #create constraints
        for groupName, par_constraint in self.extConstraints.items():
            var1 = par_constraint[0: par_constraint.find("?")].strip()
            var2 = par_constraint[par_constraint.find("(") +1 : par_constraint.rfind(")") ].strip()
            if "||" in var2:
                if len(var2[:var2.find("||")].strip() ) > 1:
                    self.__add_constraint_to_model(var1, var2[:var2.find("||")].strip() )

                if len(var2[var2.find(")"):].strip() ) > 1:
                    if "||" in var2[var2.find(")")+1:].strip():
                        orMembers = var2[var2.find("||") + 2 : var2.find(")")].replace("(","").replace(")","").strip().split(" ")
                        if len(orMembers) == 1 :
                            self.feature_builder.add_an_edge(var1, orMembers[0])
                        else:
                            self.__add_constraint_to_model(var1, orMembers, "||")
                    else:
                        self.__add_constraint_to_model(var1, var2[var2.find(")")+1:].strip() )

                orMembers = var2[var2.find("||") + 2 : var2.find(")")].replace("(","").replace(")","").strip().split(" ")

                #special case of constraint with single useflag inside a group
                if len(orMembers) == 1 :
                    self.feature_builder.add_an_edge(var1, orMembers[0])
                else:
                    self.__add_constraint_to_model(var1, orMembers, "||")

            elif "^^" in var2:
                if len(var2[:var2.find("^^")].strip() ) > 1:
                    self.__add_constraint_to_model(var1, var2[:var2.find("^^")].strip() )

                if len(var2[var2.find(")"):].strip() ) > 1:
                    if "^^" in var2[var2.find(")")+1:].strip():
                        orMembers = var2[var2.find("^^") + 2 : var2.find(")")].replace("(","").replace(")","").strip().split(" ")
                        if len(orMembers) == 1 :
                            self.feature_builder.add_an_edge(var1, orMembers[0])
                        else:
                            self.__add_constraint_to_model(var1, orMembers, "^^")
                    else:
                        self.__add_constraint_to_model(var1, var2[var2.find(")")+1:].strip() )

                xorMembers = var2[var2.find("^^") + 2 : var2.find(")")].replace("(","").replace(")","").strip().split(" ")

                #special case of constraint with single useflag inside a group
                if len(xorMembers) == 1 :
                    self.feature_builder.add_an_edge(var1, xorMembers[0])
                else:
                    self.__add_constraint_to_model(var1, xorMembers, "^^")

            elif "??" in var2:
                if len(var2[:var2.find("??")].strip() ) > 1:
                    self.__add_constraint_to_model(var1, var2[:var2.find("??")].strip() )

                if len(var2[var2.find(")"):].strip() ) > 1:
                    if "??" in var2[var2.find(")")+1:].strip():
                        orMembers = var2[var2.find("??") + 2 : var2.find(")")].replace("(","").replace(")","").strip().split(" ")
                        if len(orMembers) == 1 :
                            self.feature_builder.add_an_edge(var1, orMembers[0])
                        else:
                            self.__add_constraint_to_model(var1, orMembers, "??")
                    else:
                        self.__add_constraint_to_model(var1, var2[var2.find(")")+1:].strip() )

                mayMembers = var2[var2.find("??") + 2 : var2.find(")")].replace("(","").replace(")","").strip().split(" ")

                #special case of constraint with single useflag inside a group
                if len(mayMembers) == 1 :
                    self.feature_builder.add_an_edge(var1, mayMembers[0])
                else:
                    self.__add_constraint_to_model(var1, mayMembers, "??")
            
            else:
                if "?" in var2:
                    self.__add_constraint_to_model(var1, var2, "")
                else:
                    for flag in var2.strip().split(" "):
                        self.__add_constraint_to_model(var1, flag, "") if len(flag.strip()) > 1 else log.debug("complex constraint: " + self.packageName)

    def __create_relations_and_groups(self):
        #create parent child relations
        for parent in self.parents.keys():
            for child in self.parents[parent]:
                self.feature_builder.add_an_edge(parent, child)

        #create OR groups
        for groupName, groupMembers in self.ORgrouping.items():
            parent = self.__checkParentsOfGroup(groupMembers)
            #if only one parent of the OR group, then create an OR group
            if len(parent) == 1:
                self.feature_builder.make_binary_feature(groupName, False)
                self.feature_builder.add_an_edge(parent[0], groupName)
                for groupMem in groupMembers:
                    self.feature_builder.add_an_edge(groupName, groupMem)
                self.feature_builder.emplace_relationship(groupName, "OR")
            #else add them as an OR constraint 
            elif len(parent) > 1:
                self.__add_constraint_to_model(self.packageName, groupMembers, "||")

        #create XOR groups
        for groupName, groupMembers in self.XORgrouping.items():
            parent = self.__checkParentsOfGroup(groupMembers)
            #if only one parent of the XOR group, then create an XOR group
            if len(parent) == 1:
                self.feature_builder.make_binary_feature(groupName, False)
                self.feature_builder.add_an_edge(parent[0], groupName)
                for groupMem in groupMembers:
                    self.feature_builder.add_an_edge(groupName, groupMem)
                self.feature_builder.emplace_relationship(groupName, "XOR")
            #else add them as an XOR constraint 
            elif len(parent) > 1:
                self.__add_constraint_to_model(self.packageName, groupMembers, "^^")

        #create MAYBE groups
        for groupName, groupMembers in self.MAYgrouping.items():
            parent = self.__checkParentsOfGroup(groupMembers)
            #if only one parent of the MAYBE group, then create an XOR group with optional feature group parent
            if len(parent) == 1:
                self.feature_builder.make_binary_feature(groupName, True)
                self.feature_builder.add_an_edge(parent[0], groupName)
                for groupMem in groupMembers:
                    self.feature_builder.add_an_edge(groupName, groupMem)
                self.feature_builder.emplace_relationship(groupName, "XOR")
            #else add them as an MAYBE constraint 
            elif len(parent) > 1:
                self.__add_constraint_to_model(self.packageName, groupMembers, "??")

    def __checkParentsOfGroup(self, group):
        group_parent = list()
        for flag in group:
            for parent, child in self.parents.items():
                if flag in child:
                    group_parent.append(parent)    
        
        return list(set(group_parent))

    def __constraintParser(self, constraint):
        constraint.strip()
        #base condition, if the constraint is just useflag then return it as is
        if (
                "?" not in constraint  
            and "||" not in constraint
            and "^^" not in constraint
            and "??" not in constraint
        ) : 
            return constraint.strip().split(" ")
        
        #else recurviely check constraints and add them to their relevant dictionaries
        else:
            var1 = constraint[0:constraint.find("?")].strip()
            var2 = constraint[constraint.find("(")+1: constraint.rfind(")")-1].strip()

            #check if its simple not 
            if "!" in var2 or "!" in var1:
                self.extConstraints["extConstraint_"+str(self.extCounter)]  = constraint
                self.extCounter = self.extCounter + 1 

            #check multiple reqUse concatinated inside var2
            elif "?" in var2[var2.find("?")+1:]:
                self.extConstraints["extConstraint_"+str(self.extCounter)]  = constraint
                self.extCounter = self.extCounter + 1 
            
            #check if the internal condition has OR group
            elif "||" in var2:
                self.extConstraints["extConstraint_"+str(self.extCounter)]  = constraint
                self.extCounter = self.extCounter + 1 
                
            #check if the internal condition has XOR group
            elif "^^" in var2:
                self.extConstraints["extConstraint_"+str(self.extCounter)]  = constraint
                self.extCounter = self.extCounter + 1 
            
            #check if the internal condition has MAY group
            elif "??" in var2:
                self.extConstraints["extConstraint_"+str(self.extCounter)]  = constraint
                self.extCounter = self.extCounter + 1 
            
            #default recursive check
            else:
                var3 = self.__constraintParser(var2)
                if len(var3) >1:
                    for var in var3:
                        self.parents[var].append(var1)        
                else:
                    self.parents[var3[0]].append(var1)
            

            return var1.strip().split(" ")
            
    def __add_constraint_to_model(self, var1, var2, group = ""):
        cb = vf.constraint.ConstraintBuilder()
        
        #check if the feature is negated
        if "!" in var1:
            var1 = var1.replace("!", "")
            cb.lNot().feature(var1)
        else:
            cb.feature(var1)
        
        #check for OR group
        if group == "||":
            cb.implies().openPar()
            for i in range(len(var2)-1):
                cb.lNot().feature(var2[i].replace("!","")).lOr() if "!" in var2[i] else cb.feature(var2[i]).lOr()
                
            cb.lNot().feature(var2[i+1].replace("!","")).closePar() if "!" in var2[i+1] else cb.feature(var2[i+1]).closePar()
            self.feature_builder.add_boolean_constraint(cb.build())

        #check for XOR group
        elif group == "^^":
            cb.implies().openPar()
            for i in range(len(var2)-1):
                cb.lNot().feature(var2[i].replace("!","")).lXor() if "!" in var2[i] else cb.feature(var2[i]).lXor()
                
            cb.lNot().feature(var2[i+1].replace("!","")).closePar() if "!" in var2[i+1] else cb.feature(var2[i+1]).closePar()
            self.feature_builder.add_boolean_constraint(cb.build())

        #check for MAYBE group (a MAYBE group is essentially an optional XOR)
        elif group == "??":
            parent = self.__checkParentsOfGroup(var2)
            groupName = "abs_opt_xor_grp_"+str(self.xorCounter)
            #if only one parent of the XOR group, then create an XOR group
            if len(parent) == 1:
                self.feature_builder.make_binary_feature(groupName, True)        
                self.feature_builder.add_an_edge(parent[0], groupName)
                for groupMem in var2:
                    self.feature_builder.add_an_edge(groupName, groupMem)
                self.feature_builder.emplace_relationship(groupName, "XOR")
                self.xorCounter = self.xorCounter + 1
            #else add them as an XOR constraint 
            elif len(parent) > 1:
                log.debug("complex constraint in: " + self.packageName)
            
            cb.implies().feature(groupName)
            self.feature_builder.add_boolean_constraint(cb.build())
            
        
        #no group found, check for implication symbol, prase the useflags
        elif group == "" :
            if "?" in var2:
                var1_in_var2 = var2[:var2.find("?")].strip()
                var2_in_var2 = var2[var2.find("(")+1:var2.rfind(")")].strip()
                lst_var2_in_var2 = var2_in_var2.split(" ")
                
                cb.implies().openPar().lNot().feature(var1_in_var2.replace("!","")).implies() if "!" in var1_in_var2 else cb.implies().openPar().feature(var1_in_var2).implies()
                if len(lst_var2_in_var2) > 1:
                    cb.openPar()
                    for i in range(len(lst_var2_in_var2)-1): 
                        cb.lNot().feature(lst_var2_in_var2[i].replace("!","")).lAnd() if "!" in lst_var2_in_var2[i] else cb.feature(lst_var2_in_var2[i]).lAnd()
                    
                    cb.lNot().feature(lst_var2_in_var2[i+1].replace("!","")).closePar().closePar() if "!" in lst_var2_in_var2[i+1] else cb.feature(lst_var2_in_var2[i+1]).closePar().clsosePar()
                else:
                    cb.lNot().feature(var2_in_var2.replace("!","")).closePar() if "!" in var2_in_var2 else cb.feature(var2_in_var2).closePar()
                
                self.feature_builder.add_boolean_constraint(cb.build())
            else:
                lst_var2 = var2.strip().split(" ")
                if len(lst_var2) > 1:
                    cb.implies().openPar()
                    for i in range(len(lst_var2)-1):
                        cb.lNot().feature(lst_var2[i].replace("!","")).lAnd() if "!" in lst_var2[i] else cb.feature(lst_var2[i]).lAnd()
                    cb.lNot().feature(lst_var2[i+1].replace("!","")).closePar() if "!" in lst_var2[i+1] else cb.feature(lst_var2[i+1]).closePar()

                else:
                    cb.implies().lNot().feature(var2.replace("!", "")) if "!" in var2 else cb.implies().feature(var2)
                self.feature_builder.add_boolean_constraint(cb.build())

    def __constraintModifier(self, constraint, excludeFeature):
        if excludeFeature not in constraint:
            return constraint
        else:
            if ord(constraint.strip()[0]) == 124 or ord(constraint.strip()[0]) == 94 or ord(constraint.strip()[0]) == 63 :
                checkConstraint = constraint[constraint.find("(")+1 : constraint.find(")")-1].replace(excludeFeature, "").strip().split(" ")
                if len(checkConstraint) > 0 and checkConstraint[0] != '':
                    constraint = constraint.replace(excludeFeature, "").replace("  ", " ").replace("+","")
                else:
                    return None
            else:
                var1 = constraint[0:constraint.find("?")].strip()
                var2 = constraint[constraint.find("(")+1: constraint.rfind(")")-1].strip()
                
                if excludeFeature in var1:
                    return None
                elif len(var2.replace(excludeFeature, "").strip().split(" ")) > 0 and var2.replace(excludeFeature, "").strip().split(" ")[0] == '':
                    return None
                else:
                    constraint = constraint.replace(var2, var2.replace(excludeFeature, "") ).replace("  ", " ").replace("+","")      
        return constraint


    ##################### main functions #####################
    ####### function to parse the entire required_use variable and useflag string #######
    def parser(self, reqUse, useflagStr, excludeFeature=None):
        self.parents[self.packageName] = list()

        constraints = list()
        s_pointer = 0
        b_counter = 1

        #simple iteration to strip useflags and constraints
        for i in range(reqUse.find("(")+1, len(reqUse)):
            if   reqUse[i] == "(" : b_counter = b_counter+1
            elif reqUse[i] == ")" : 
                b_counter = b_counter-1
                if b_counter == 0:
                    constraints.append(reqUse[s_pointer:i+1].strip())
                    s_pointer = i+1
                
        #check for relations, add them to groups and create constraints
        for constraint in constraints:
            if excludeFeature != None:
                constraint = self.__constraintModifier(constraint, excludeFeature)
        
            if constraint != None:
                if ord(constraint.strip()[0]) == 124:
                    self.ORgrouping["abs_or_grp_"+str(self.orCounter)] = constraint[constraint.find("(")+1 : constraint.find(")")-1].strip().split(" ")
                    self.orCounter = self.orCounter + 1
                elif ord(constraint.strip()[0]) == 94:
                    self.XORgrouping["abs_xor_grp_"+str(self.xorCounter)] = constraint[constraint.find("(")+1 : constraint.find(")")-1].strip().split(" ")
                    self.xorCounter = self.xorCounter + 1
                elif ord(constraint.strip()[0]) == 63:
                    self.MAYgrouping["abs_may_grp_"+str(self.mayCounter)] = constraint[constraint.find("(")+1 : constraint.find(")")-1].strip().split(" ")
                    self.mayCounter = self.mayCounter + 1
                else:
                    self.__constraintParser(constraint)
           
        #updating default counters
        self.useflags = useflagStr.strip().split(" ") 
        for i in range(0, len(self.useflags)):
            if self.useflags[i].startswith("+") == True:
                self.useflags[i] = self.useflags[i][1:] 
                self.defaultCounter = self.defaultCounter + 1

        #handle missing childs from parents
        #self.useflags = useflagStr.strip().replace("+", "").split(" ") 
        parentuseflags = self.useflags.copy()

        #every useflag that has no parent, assign it to root
        for parent, childList in self.parents.items():
            for child in childList:
                if child.replace("!", "").strip() in parentuseflags:
                    parentuseflags.remove(child)

        #add all flags that are not in useflags to root 
        for parent, childList in self.parents.items():
            for child in childList:
                if child not in self.useflags and "!" not in child:
                    self.useflags.append(child)
                    #useflags_with_defaults.append(child)

        self.parents[self.packageName] = parentuseflags

    ####### create feature models using the vara-feature library #######
    def createFeatureModel(self, packageName, reqUse, useflagStr):
        self.packageName = packageName
        log.debug("creating feature model for: "+self.packageName)

        #special cases for keywords as useflags
        if "amd64" in reqUse and " amd64 " not in useflagStr:
            useflagStr = useflagStr + " amd64"
            log.debug("added amd64 to: "+self.packageName)

        if "arm" in reqUse and " arm " not in useflagStr:
            useflagStr = useflagStr + " arm"
            log.debug("added arm to: "+self.packageName)

        if "x86" in reqUse and " x86 " not in useflagStr:
            useflagStr = useflagStr + " x86"
            log.debug("added x86 to: "+self.packageName)

        if "kernel_linux" in reqUse and "kernel_linux" not in useflagStr:
            useflagStr = useflagStr + " kernel_linux"
            log.debug("added kernel_linux to: "+self.packageName)
        
        # extract relations, create feature model
        try:
            # parsing relationships from reqUse and useflagStr
            self.parser(reqUse, useflagStr)

            # removing duplicates in the useflags string (shouldnt be there but just in case :)) 
            self.useflags = list(set(self.useflags))
    
            # create features, relations, and constraints
            self.__create_features()
            self.__create_relations_and_groups()
            self.__create_constraints()
            
            # create feature model
            self.feature_model = self.feature_builder.build_feature_model()
            
            # commented code for logging into JSON
            """
            ####### logs for analysis
            log.debug("number of useflags: "        + str(len(self.useflags)))
            log.debug("number of defaults: "        + str(self.defaultCounter))
            log.debug("number of ORgrouping: "      + str(len(self.ORgrouping)))
            log.debug("number of XORgrouping: "     + str(len(self.XORgrouping)))
            log.debug("number of MAYgrouping: "     + str(len(self.MAYgrouping)))
            log.debug("number of extConstraints: "  + str(len(self.extConstraints)))
            log.debug("number of configs: "         + str(len(vf.configuration.getAllConfigs(self.feature_model))))
            #log.debug("size:"                       + str(self.feature_model.size()))

            ####### writing for json
            data = {
                'name': packageName,
                'no_of_useflags'        :str(len(self.useflags)),
                'no_of_defaults'        :str(self.defaultCounter),
                'no_of_ORgrouping'      :str(len(self.ORgrouping)),
                'no_of_XORgrouping'     :str(len(self.XORgrouping)),
                'no_of_MAYgrouping'     :str(len(self.MAYgrouping)),
                'no_of_extConstraints'  :str(len(self.extConstraints)),
                'no_of_configs'         :str(len(vf.configuration.getAllConfigs(self.feature_model))),
                'depth'                 :0
                #'size'                  :str(self.feature_model.size())
            }

            with open('descriptives.json', 'a') as outputFile:
                json.dump(data, outputFile, indent=4, separators = (',', ': '))
            """
        except Exception as e:
            log.error(self.packageName + " failed with: " + str(e))
            
        ####### view() function from vara feature library to show the feature model created directly
        #self.feature_model.view()

        ####### writer to write the feature model as an XML file
        #writer = vf.fm_writer.FeatureModelXmlWriter(self.feature_model)
        #writer.write_feature_model_to_file("vara_example_package.xml")

        return self.feature_model, self.packageName

    ####### function for getting the details about a package without creating a feature model #######
    def getDetails(self, packageName, reqUse, useflagStr):
        # parsing relationships from reqUse and useflagStr
        self.parser(reqUse, useflagStr)

        # removing duplicates in the useflags (shouldnt be there but just in case :) 
        self.useflags = list(set(self.useflags))
        
        # logs for analysis
        data = {
            'name': packageName,
            'no_of_useflags'        :str(len(self.useflags)),
            'no_of_defaults'        :str(self.defaultCounter),
            'no_of_ORgrouping'      :str(len(self.ORgrouping)),
            'no_of_XORgrouping'     :str(len(self.XORgrouping)),
            'no_of_MAYgrouping'     :str(len(self.MAYgrouping)),
            'no_of_extConstraints'  :str(len(self.extConstraints)),
            'depth'                 :0,
            'size'                  :str(self.feature_model.size())

        }

        """ 
        with open('descriptives.json', 'a') as outputFile:
            json.dump(data, outputFile, indent=4, separators = (',', ': '))
        """
        return data

    ####### function that removes a specific useflag and all the constraint that contain it. 
    def createFeatureModel_withoutaFeature(self, packageName, reqUse, useflagStr, excludeFeature):
        self.packageName = packageName
        log.debug("creating feature model for: "+self.packageName)

        # special cases for keywords as useflags
        if "amd64" in reqUse and " amd64 " not in useflagStr:
            useflagStr = useflagStr + " amd64"
            log.debug("added amd64 to: "+self.packageName)

        if "arm" in reqUse and " arm " not in useflagStr:
            useflagStr = useflagStr + " arm"
            log.debug("added arm to: "+self.packageName)

        if "x86" in reqUse and " x86 " not in useflagStr:
            useflagStr = useflagStr + " x86"
            log.debug("added x86 to: "+self.packageName)

        if "kernel_linux" in reqUse and "kernel_linux" not in useflagStr:
            useflagStr = useflagStr + " kernel_linux"
            log.debug("added kernel_linux to: "+self.packageName)
        
        # extract relations, create feature model
        try:
            # parsing relationships from reqUse and useflagStr
            useflagStr = useflagStr.replace("+"+excludeFeature,"").replace(excludeFeature,"").replace("  ", " ")
            self.parser(reqUse, useflagStr, excludeFeature)

            # removing duplicates in the useflags (shouldnt be there but just in case :) 
            self.useflags = list(set(self.useflags))
            
            # create features, relations, and constraints
            self.__create_features()
            self.__create_relations_and_groups()
            self.__create_constraints()
            
            # create feature model
            self.feature_model = self.feature_builder.build_feature_model()
            
            # logs for analysis
            log.debug("number of useflags: "        + str(len(self.useflags)))
            log.debug("number of defaults: "        + str(self.defaultCounter))
            log.debug("number of ORgrouping: "      + str(len(self.ORgrouping)))
            log.debug("number of XORgrouping: "     + str(len(self.XORgrouping)))
            log.debug("number of MAYgrouping: "     + str(len(self.MAYgrouping)))
            log.debug("number of extConstraints: "  + str(len(self.extConstraints)))
            log.debug("number of configs: "         + str(len(vf.configuration.getAllConfigs(self.feature_model))))
            #log.debug("size:"                       + str(self.feature_model.size()))

            #commented code for logging the details into JSON file
            """
            ####### writing for json
            data = {
                'name': packageName,
                'no_of_useflags'        :str(len(self.useflags)),
                'no_of_defaults'        :str(self.defaultCounter),
                'no_of_ORgrouping'      :str(len(self.ORgrouping)),
                'no_of_XORgrouping'     :str(len(self.XORgrouping)),
                'no_of_MAYgrouping'     :str(len(self.MAYgrouping)),
                'no_of_extConstraints'  :str(len(self.extConstraints)),
                'depth'                 :0
                #'size'                  :str(self.feature_model.size())
            }

            #with open('descriptives.json', 'a') as outputFile:
            #    json.dump(data, outputFile, indent=4, separators = (',', ': '))        
            """
        except Exception as e:
            log.error(self.packageName + " failed with: " + str(e))

        return self.feature_model, self.packageName

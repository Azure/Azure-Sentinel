from validate_email import validate_email
from Utils import executeProcess
from NodeEdge import Node, DrawableNode
from functools import lru_cache


class User(DrawableNode):

    def __init__(self, name, email, objectId):
        self.name = name
        self.email = email
        self.objectId = objectId

    def getNode(self):
        return Node(self.objectId, self.name, "User")

    @staticmethod
    @lru_cache(maxsize=100)
    def getUserById(userId):
        rawoutput = executeProcess(
            f'az ad user show --id {userId} --query [displayName,mail,objectId] --output tsv'.split(' '))
        output = rawoutput.split('\n')
        if len(output) != 3:
            raise Exception(
                f'Unable to get AAD User with Id - {userId}. Error - {rawoutput}')
        else:
            user = User(output[0], output[1], output[2])
            return user

    @staticmethod
    @lru_cache(maxsize=100)
    def getUserByEmail(userEmail):
        rawoutput = executeProcess(
            f'az ad user list --filter startswith(mail,\'{userEmail}\') --query [0].{{Name:displayName,Email:mail,ObjectId:objectId}} --output tsv'.split(' '))
        output = rawoutput.split('\t')
        if len(output) != 3:
            raise Exception(
                f'Not found - User with email - {userEmail}.')
        else:
            user = User(output[0], output[1], output[2])
            return user

    @staticmethod
    def getUserByIdOrEmail(userIdOrEmail):
        try:
            return User.getUserById(userIdOrEmail)
        except:
            isvalidEmail = validate_email(userIdOrEmail)
            if isvalidEmail:
                return User.getUserByEmail(userIdOrEmail)
            raise


class Group(DrawableNode):
    def __init__(self, name, email, groupId):
        self.name = name
        self.email = email
        self.groupId = groupId

    def getNode(self):
        return Node(self.groupId, self.name, "Group")

    @staticmethod
    @lru_cache(maxsize=100)
    def getGroupById(groupId):
        rawoutput = executeProcess(
            f'az ad group show --group {groupId} --query [displayName,mail,objectId] --output tsv'.split(' '))
        output = rawoutput.split('\n')
        if len(output) != 3:
            raise Exception(
                f'Unable to get AAD Group with Id - {groupId}. Error - {rawoutput}')
        else:
            group = Group(output[0], output[1], output[2])
            return group


class ServicePrincipal(DrawableNode):
    def __init__(self, name, objectId):
        self.name = name
        self.objectId = objectId

    def getNode(self):
        return Node(self.objectId, self.name, "ServicePrincipal")

    @staticmethod
    @lru_cache(maxsize=100)
    def getServicePrincipalById(objectId):
        rawoutput = executeProcess(
            f'az ad sp show --id {objectId} --query [displayName,objectId] --output tsv'.split(' '))
        output = rawoutput.split('\n')
        if len(output) != 2:
            raise Exception(
                f'Unable to get AAD ServicePrincipal with Id - {objectId}. Error - {rawoutput}')
        else:
            sp = ServicePrincipal(output[0], output[1])
            return sp


class Subscription(DrawableNode):

    def __init__(self, name, subId):
        self.name = name
        self.subId = subId

    def getNode(self):
        return Node(self.subId, self.name, "AzureSubscription")

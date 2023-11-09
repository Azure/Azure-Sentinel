class EntityId:
    """EntityId.

    It identifies an entity by its name and its key.
    """

    def __init__(self, name: str, key: str):
        """Instantiate an EntityId object.

        Identifies an entity by its name and its key.

        Parameters
        ----------
        name: str
            The entity name
        key: str
            The entity key

        Raises
        ------
            ValueError: If the entity name or key are the empty string
        """
        if name == "":
            raise ValueError("Entity name cannot be empty")
        if key == "":
            raise ValueError("Entity key cannot be empty")
        self.name: str = name
        self.key: str = key

    @staticmethod
    def get_scheduler_id(entity_id: 'EntityId') -> str:
        """Produce a SchedulerId from an EntityId.

        Parameters
        ----------
        entity_id: EntityId
            An EntityId object

        Returns
        -------
        str:
            A SchedulerId representation of the input EntityId
        """
        return f"@{entity_id.name.lower()}@{entity_id.key}"

    @staticmethod
    def get_entity_id(scheduler_id: str) -> 'EntityId':
        """Return an EntityId from a SchedulerId string.

        Parameters
        ----------
        scheduler_id: str
            The SchedulerId in which to base the returned EntityId

        Raises
        ------
        ValueError:
            When the SchedulerId string does not have the expected format

        Returns
        -------
        EntityId:
            An EntityId object based on the SchedulerId string
        """
        sched_id_truncated = scheduler_id[1:]  # we drop the starting `@`
        components = sched_id_truncated.split("@")
        if len(components) != 2:
            raise ValueError("Unexpected format in SchedulerId")
        [name, key] = components
        return EntityId(name, key)

    @staticmethod
    def get_entity_id_url_path(entity_id: 'EntityId') -> str:
        """Print the the entity url path.

        Returns
        -------
        str:
            A url path of the EntityId
        """
        return f'entities/{entity_id.name}/{entity_id.key}'

    def __str__(self) -> str:
        """Print the string representation of this EntityId.

        Returns
        -------
        str:
            A SchedulerId-based string representation of the EntityId
        """
        return EntityId.get_scheduler_id(entity_id=self)

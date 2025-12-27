import random
from typing import List, Tuple
from config.constants import ROLE_DISTRIBUTION
from models.player import Player

class RoleGenerator:
    """Handles role generation logic"""
    
    @staticmethod
    def calculate_distribution(num_residents: int, roles: dict) -> Tuple[int, int, int, int]:
        """Calculate role distribution based on number of residents"""
        if num_residents not in ROLE_DISTRIBUTION:
            raise ValueError(f"Unsupported number of residents: {num_residents}")
        
        townsfolk, outsiders, minions, demons = ROLE_DISTRIBUTION[num_residents]
        return townsfolk, outsiders, minions, demons
    
    @staticmethod
    def adjust_for_special_roles(townsfolk: int, outsiders: int, 
                                 minions: List[str], roles: dict) -> Tuple[int, int]:
        """Adjust distribution for special roles like Baron and Godfather"""
        max_outsiders = len(roles["Outsider"])
        
        # Baron: +2 Outsiders, -2 Townsfolk (but capped by available outsiders)
        if "Baron" in minions:
            # Try to add 2 outsiders, but cap at what's available
            actual_add = min(2, max_outsiders - outsiders)
            townsfolk = max(0, townsfolk - actual_add)
            outsiders += actual_add
        
        # Godfather: 50% chance to swap 1 Townsfolk for 1 Outsider
        if "Godfather" in minions:
            if random.randint(0, 1) == 0:
                # Try to add 1 outsider if possible
                if outsiders < max_outsiders:
                    townsfolk = max(0, townsfolk - 1)
                    outsiders += 1
            else:
                townsfolk += 1
                outsiders = max(0, outsiders - 1)
        
        return townsfolk, outsiders
    
    @staticmethod
    def generate_roles(num_residents: int, num_travelers: int, 
                      script_roles: dict) -> Tuple[List[Player], List[str]]:
        """
        Generate roles for all players
        Returns: (list of Players, list of 3 bluff roles)
        """
        # Get initial distribution
        townsfolk, outsiders, minions, demons = RoleGenerator.calculate_distribution(
            num_residents, script_roles
        )
        
        # Sample minions first (needed for special role checks)
        sampled_minions = random.sample(script_roles["Minion"], minions)
        
        # Adjust for special roles
        townsfolk, outsiders = RoleGenerator.adjust_for_special_roles(
            townsfolk, outsiders, sampled_minions, script_roles
        )
        
        # Sample final roles
        try:
            final_townsfolk = random.sample(script_roles["Townsfolk"], townsfolk)
            final_outsiders = random.sample(script_roles["Outsider"], outsiders)
            final_demons = random.sample(script_roles["Demon"], demons)
        except ValueError as e:
            raise ValueError(f"Not enough roles to sample: {e}")
        
        # Create role pool for residents
        role_pool = final_townsfolk + final_outsiders + sampled_minions + final_demons
        
        # Handle Marionette seating requirement
        has_marionette = "Marionette" in sampled_minions
        if has_marionette:
            # Remove Marionette and Demon from pool temporarily
            role_pool.remove("Marionette")
            demon_role = final_demons[0]
            role_pool.remove(demon_role)
            
            # Shuffle the rest
            random.shuffle(role_pool)
            
            # Pick a random position for the Demon (not first or last to have neighbors)
            demon_pos = random.randint(1, num_residents - 2)
            
            # Insert Demon at chosen position
            role_pool.insert(demon_pos, demon_role)
            
            # Insert Marionette next to Demon (randomly left or right)
            marionette_offset = random.choice([-1, 1])
            role_pool.insert(demon_pos + (1 if marionette_offset == 1 else 0), "Marionette")
        else:
            # Normal shuffling if no Marionette
            random.shuffle(role_pool)
        
        # Create traveler pool
        traveler_roles = script_roles.get("Traveler", [])[:]
        random.shuffle(traveler_roles)
        
        # Assign roles to players
        players = []
        assigned_roles = []
        
        for i in range(num_residents + num_travelers):
            is_traveler = i >= num_residents
            
            if not is_traveler:
                role = role_pool.pop(0)  # Pop from front since we've arranged the order
                player_class = RoleGenerator._get_role_class(role, script_roles)
            else:
                role = traveler_roles.pop() if traveler_roles else "Traveler"
                player_class = "Traveler"
            
            player = Player(
                username="",  # Will be filled by UI
                role=role,
                player_class=player_class,
                is_traveler=is_traveler
            )
            
            players.append(player)
            assigned_roles.append(role)
        
        # Handle Drunk fake roles
        available_fake_roles = [r for r in script_roles["Townsfolk"] 
                               if r not in assigned_roles]
        random.shuffle(available_fake_roles)  # FIX: Shuffle the list before popping
        
        for player in players:
            if player.role == "Drunk":
                fake_role = available_fake_roles.pop() if available_fake_roles else "unknown"
                player.drunk_fake_role = fake_role
                player.role = f"Drunk-{fake_role}"
        
        # Generate bluff roles
        bluff_pool = [r for r in script_roles["Townsfolk"] + script_roles["Outsider"] 
                     if r not in assigned_roles]
        random.shuffle(bluff_pool)
        bluff_roles = [bluff_pool.pop() if bluff_pool else "TBD" for _ in range(3)]
        
        return players, bluff_roles
    
    @staticmethod
    def _get_role_class(role: str, script_roles: dict) -> str:
        """Determine the class of a role"""
        for role_type in ["Townsfolk", "Outsider", "Minion", "Demon"]:
            if role in script_roles[role_type]:
                return role_type
        return "Unknown"
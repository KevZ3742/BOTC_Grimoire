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
            final_demons = random.sample(script_roles["Demon"], demons)
            final_outsiders = random.sample(script_roles["Outsider"], outsiders)
        except ValueError as e:
            raise ValueError(f"Not enough roles to sample: {e}")
        
        # Check if Atheist was actually selected in THIS game
        has_atheist = "Atheist" in final_townsfolk
        
        if has_atheist:
            # Atheist game: replace all evil roles with good roles
            return RoleGenerator._generate_atheist_game(
                num_residents, num_travelers, script_roles, final_townsfolk, final_outsiders
            )
        
        # Normal game generation continues...
        # Create role pool for residents
        role_pool = final_townsfolk + final_outsiders + sampled_minions + final_demons
        
        # Handle Marionette seating requirement
        has_marionette = "Marionette" in sampled_minions
        if has_marionette:
            # Remove Marionette and Demon from pool temporarily
            role_pool.remove("Marionette")
            demon_role = final_demons[0]
            role_pool.remove(demon_role)
            
            # Shuffle the rest (this will be num_residents - 2 roles)
            random.shuffle(role_pool)
            
            # Pick a random position for the Demon (can be anywhere in circle)
            demon_pos = random.randint(0, num_residents - 1)
            
            # Calculate neighbor positions (treating as circular)
            # We want Marionette to be adjacent to Demon in final arrangement
            left_neighbor = (demon_pos - 1) % num_residents
            right_neighbor = (demon_pos + 1) % num_residents
            
            # Randomly choose left or right neighbor
            marionette_pos = random.choice([left_neighbor, right_neighbor])
            
            # Insert them in order: lower index first to avoid shifting issues
            if demon_pos < marionette_pos:
                role_pool.insert(demon_pos, demon_role)
                role_pool.insert(marionette_pos, "Marionette")
            else:
                role_pool.insert(marionette_pos, "Marionette")
                role_pool.insert(demon_pos, demon_role)
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
        random.shuffle(available_fake_roles)  # Shuffle the list before popping
        
        for player in players:
            if player.role == "Drunk":
                fake_role = available_fake_roles.pop() if available_fake_roles else "unknown"
                player.drunk_fake_role = fake_role
                player.role = f"Drunk-{fake_role}"
        
        # Handle Evil Twin - mark a random good player as the twin
        has_evil_twin = "Evil Twin" in sampled_minions
        if has_evil_twin:
            # Find all good players (Townsfolk or Outsider, not travelers)
            good_players = [p for p in players 
                          if not p.is_traveler and p.player_class in ["Townsfolk", "Outsider"]]
            
            if good_players:
                # Select a random good player to be the Evil Twin's twin
                twin_player = random.choice(good_players)
                # Mark them by appending "-Evil Twin" to their role
                twin_player.role = f"{twin_player.role}-Evil Twin"
        
        # Generate bluff roles
        bluff_pool = [r for r in script_roles["Townsfolk"] + script_roles["Outsider"] 
                     if r not in assigned_roles]
        random.shuffle(bluff_pool)
        bluff_roles = [bluff_pool.pop() if bluff_pool else "N/A" for _ in range(3)]
        
        return players, bluff_roles
    
    @staticmethod
    def _generate_atheist_game(num_residents: int, num_travelers: int, 
                               script_roles: dict, 
                               already_sampled_townsfolk: List[str],
                               already_sampled_outsiders: List[str]) -> Tuple[List[Player], List[str]]:
        """
        Generate an Atheist game where everyone is good (Townsfolk/Outsiders)
        The Atheist role is already in already_sampled_townsfolk
        """
        # Start with what we already sampled
        final_roles = already_sampled_townsfolk[:] + already_sampled_outsiders[:]
        assigned_roles = final_roles[:]
        
        # We need to fill the remaining slots (demons + minions) with more good roles
        townsfolk, outsiders, minions, demons = RoleGenerator.calculate_distribution(
            num_residents, script_roles
        )
        
        # Calculate how many more roles we need (to replace demons and minions)
        additional_needed = minions + demons
        
        # Get available roles (excluding what's already assigned)
        available_townsfolk = [r for r in script_roles["Townsfolk"] 
                               if r not in assigned_roles]
        available_outsiders = [r for r in script_roles["Outsider"] 
                              if r not in assigned_roles]
        
        # Try to maintain roughly 2:1 townsfolk to outsiders ratio for the additional roles
        target_additional_outsiders = min(additional_needed // 3, len(available_outsiders))
        target_additional_townsfolk = additional_needed - target_additional_outsiders
        
        # Adjust if we don't have enough
        if target_additional_townsfolk > len(available_townsfolk):
            overflow = target_additional_townsfolk - len(available_townsfolk)
            target_additional_townsfolk = len(available_townsfolk)
            target_additional_outsiders = min(target_additional_outsiders + overflow, 
                                             len(available_outsiders))
        
        if target_additional_outsiders > len(available_outsiders):
            overflow = target_additional_outsiders - len(available_outsiders)
            target_additional_outsiders = len(available_outsiders)
            target_additional_townsfolk = min(target_additional_townsfolk + overflow, 
                                             len(available_townsfolk))
        
        try:
            # Sample additional roles
            if target_additional_townsfolk > 0:
                extra_townsfolk = random.sample(available_townsfolk, target_additional_townsfolk)
                final_roles.extend(extra_townsfolk)
                assigned_roles.extend(extra_townsfolk)
            
            if target_additional_outsiders > 0:
                extra_outsiders = random.sample(available_outsiders, target_additional_outsiders)
                final_roles.extend(extra_outsiders)
                assigned_roles.extend(extra_outsiders)
        except ValueError as e:
            raise ValueError(f"Not enough good roles for Atheist game: {e}")
        
        # Shuffle the role pool
        random.shuffle(final_roles)
        
        # Create traveler pool
        traveler_roles = script_roles.get("Traveler", [])[:]
        random.shuffle(traveler_roles)
        
        # Assign roles to players
        players = []
        
        for i in range(num_residents + num_travelers):
            is_traveler = i >= num_residents
            
            if not is_traveler:
                role = final_roles.pop(0)
                player_class = RoleGenerator._get_role_class(role, script_roles)
            else:
                role = traveler_roles.pop() if traveler_roles else "Traveler"
                player_class = "Traveler"
            
            player = Player(
                username="",
                role=role,
                player_class=player_class,
                is_traveler=is_traveler
            )
            
            players.append(player)
        
        # Handle Drunk fake roles (if any Drunks in the game)
        available_fake_roles = [r for r in script_roles["Townsfolk"] 
                               if r not in assigned_roles]
        random.shuffle(available_fake_roles)
        
        for player in players:
            if player.role == "Drunk":
                fake_role = available_fake_roles.pop() if available_fake_roles else "unknown"
                player.drunk_fake_role = fake_role
                player.role = f"Drunk-{fake_role}"
        
        # Generate bluff roles - in Atheist game, there are no evil players
        # So bluffs might not have many options or might be N/A
        bluff_pool = [r for r in script_roles["Townsfolk"] + script_roles["Outsider"] 
                     if r not in assigned_roles]
        random.shuffle(bluff_pool)
        bluff_roles = [bluff_pool.pop() if bluff_pool else "N/A" for _ in range(3)]
        
        return players, bluff_roles
    
    @staticmethod
    def _get_role_class(role: str, script_roles: dict) -> str:
        """Determine the class of a role"""
        for role_type in ["Townsfolk", "Outsider", "Minion", "Demon"]:
            if role in script_roles[role_type]:
                return role_type
        return "Unknown"
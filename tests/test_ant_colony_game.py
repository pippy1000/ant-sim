import unittest

from ant_colony_game.game import ColonyGame


class AntColonyGameTests(unittest.TestCase):
    def test_game_starts_with_basic_colony(self):
        game = ColonyGame()
        self.assertEqual(game.food, 10)
        self.assertEqual(game.workers, 2)
        self.assertEqual(game.soldiers, 1)
        self.assertEqual(game.nest_level, 1)

    def test_tick_increases_food(self):
        game = ColonyGame(food=10, workers=2)
        game.tick()
        self.assertGreater(game.food, 10)

    def test_hire_worker_costs_food(self):
        game = ColonyGame(food=40, workers=2)
        before = game.food
        game.hire_worker()
        self.assertLess(game.food, before)
        self.assertEqual(game.workers, 3)

    def test_upgrade_nest_increases_level(self):
        game = ColonyGame(food=100)
        game.upgrade_nest()
        self.assertGreater(game.nest_level, 1)

    def test_zero_soldiers_are_allowed_and_exposed_to_tick_logic(self):
        game = ColonyGame(food=20, workers=2, soldiers=0, enemy_pressure=2)
        game.auto_gather = False
        self.assertEqual(game.soldiers, 0)

        game.turn = 5
        before_food = game.food
        game.tick()

        self.assertEqual(game.turn, 6)
        self.assertLess(game.food, before_food)

    def test_idle_dashboard_reports_passive_income_and_toggle(self):
        game = ColonyGame(food=20, workers=2, soldiers=1)

        self.assertTrue(game.auto_gather)
        self.assertGreater(game.idle_income, 0)
        self.assertIn("Idle income", game.status())

        game.toggle_idle()
        self.assertFalse(game.auto_gather)


if __name__ == "__main__":
    unittest.main()

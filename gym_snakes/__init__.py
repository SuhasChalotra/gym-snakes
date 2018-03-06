from gym.envs.registration import register

register(
    id='Snakes-v0',
    entry_point='gym_snakes.envs:SnakesEnv',
)

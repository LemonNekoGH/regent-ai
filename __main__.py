import regent_ai
import gymnasium as gym

from stable_baselines3 import PPO


if __name__ == '__main__':
    env = gym.make(id='Regent-v0')

    # env.reset()
    # env.close()

    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)
    model.save('regent-ai-ppo-v0')

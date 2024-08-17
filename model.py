import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size,hidden_size)
        self.linear2 = nn.Linear(hidden_size,output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
    def save(self, file_name='model.pth'):
        folder_path = './model'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_name = os.path.join(folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class QTrainer:
    def __init__(self, model, lr, gamma) -> None:
        self.model = model
        self.lr = lr
        self.gamma = gamma
        self.optim = optim.Adam(model.parameters(), lr=self.lr)
        self.loss_fun = nn.MSELoss()

    def train_step(self, state, action, reward, state_new, done):
        # shape (n,x)
        state = torch.tensor(state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.float)
        state_new = torch.tensor(state_new, dtype=torch.float)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            action = torch.unsqueeze(action, 0)
            state_new = torch.unsqueeze(state_new, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # predicted Q value with current state
        pred = self.model(state)

        target = pred.clone()
        for i in range(len(done)):
            Q_new = reward[i]
            if not done[i]:
                Q_new = reward[i] + self.gamma * torch.max(self.model(state_new[i]))
                            
            target[i][torch.argmax(action).item()] = Q_new
        
        self.optim.zero_grad()
        loss = self.loss_fun(target, pred)
        loss.backward()

        self.optim.step()
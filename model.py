import torch
import torch.nn as nn
import torchvision.models as models
import numpy as np

class CNN(nn.Module):
    def __init__(self, num_classes, model='mobilenet_v2'):
        super(CNN, self).__init__()
        
        self.num_classes = num_classes
        self.chosen_model = model
        
        if self.chosen_model == 'mobilenet_v2':
            self.model = models.mobilenet_v2(weights=None) # pretrained=False, since we load weights

            self.classifier = nn.Sequential(
                nn.Dropout(0.1),
                nn.Linear(self.model.last_channel, 256, bias=False),
                nn.ReLU(),
                nn.BatchNorm1d(256),
                nn.Linear(256, 128, bias=False),
                nn.ReLU(),
                nn.BatchNorm1d(128),
                nn.Linear(128, self.num_classes, bias=False),
                nn.BatchNorm1d(self.num_classes),
            )

            self.model.classifier = self.classifier
        else:
            # In a real app, you might want to support the other models from the notebook
            raise NotImplementedError(f"Model {model} is not supported yet.")

    def forward(self, x):
        return self.model(x) 
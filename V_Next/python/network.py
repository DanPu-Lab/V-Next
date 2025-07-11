import torch
import torch.nn as nn
import torch.nn.functional as F

class SE_block(nn.Module):
    def __init__(self, channel, ratio=16):
        super(SE_block, self).__init__()
        
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc1 = nn.Linear(channel, channel // ratio, bias=False)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(channel // ratio, channel, bias=False)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.pool(x).view(b, c)
        y = self.fc1(y)
        y = self.relu(y)
        y = self.fc2(y)
        y = self.sigmoid(y)
        return y.view(b, c, 1, 1)

class Bottleneck(nn.Module):
    
    extension = 4
    
    def __init__(self, in_channel, out_channel, stride=1, groups=32, base_width=4):
        super(Bottleneck, self).__init__()
        
        width = int(out_channel * (base_width / 64.)) * groups
        
        self.conv1 = nn.Conv2d(in_channel, width, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(width)
        
        self.conv2 = nn.Conv2d(width, width, kernel_size=3, stride=stride, padding=1, groups=groups, bias=False)
        self.bn2 = nn.BatchNorm2d(width)
        
        self.conv3 = nn.Conv2d(width, out_channel * self.extension, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channel * self.extension)
        
        self.relu = nn.ReLU()
        
        self.SE = SE_block(out_channel * self.extension)
        
        self.shortcut = nn.Sequential()
        if in_channel != out_channel * self.extension:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channel, out_channel * self.extension, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channel * self.extension)
            )
            
    def forward(self, x):
        identity = self.shortcut(x)
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)
        
        out = self.conv3(out)
        out = self.bn3(out)
        out = self.relu(out)  
        
        se = self.SE(out)
        out = out * se
        
        out += identity
        out = self.relu(out) 
        
        return out

class V_NextNet(nn.Module):
    def __init__(self, channel, groups=32, base_width=4):
        super(V_NextNet, self).__init__()
        
        dim = 64
        
        self.conv1 = nn.Conv2d(channel, dim, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(dim)
        self.relu = nn.ReLU()
        
        self.layer1 = self._make_layer(dim, 64, num_blocks=3, groups=groups, base_width=base_width)
        self.layer2 = self._make_layer(64 * Bottleneck.extension, 128, num_blocks=4, groups=groups, base_width=base_width)
        self.layer3 = self._make_layer(128 * Bottleneck.extension, 256, num_blocks=6, groups=groups, base_width=base_width)
        self.layer4 = self._make_layer(256 * Bottleneck.extension, 512, num_blocks=3, groups=groups, base_width=base_width)
        
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.linear = nn.Linear(512 * Bottleneck.extension, 240)
        self.fc2 = nn.Linear(240, 4)
        self.fc3 = nn.Linear(240, 1)
        self.fc4 = nn.Linear(240, 4)

    def _make_layer(self, in_channels, out_channels, num_blocks, groups, base_width):
        layers = []
        layers.append(Bottleneck(in_channels, out_channels, groups=groups, base_width=base_width))
        for _ in range(1, num_blocks):
            layers.append(Bottleneck(out_channels * Bottleneck.extension, out_channels, groups=groups, base_width=base_width))
        return nn.Sequential(*layers)


    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        
        internal_outs = [x]

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        internal_outs.append(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.linear(x)

        out1 = self.fc2(x)
        out2 = self.fc3(x)
        out3 = self.fc4(x)

        return [out1, out2, out3], internal_outs

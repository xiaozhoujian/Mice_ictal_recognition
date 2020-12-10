import torch
from torch.utils.data import DataLoader
from torch import nn
from opts import parse_opts
from models.model import generate_model
from utils import AverageMeter
from dataset.dataset_val_min import MICE
import os
from detection.utils.torch_utils import select_device
from models.experimental import attempt_load


def validation(opts, model, val_dataloader):
    accuracies = AverageMeter()
    with torch.no_grad():
        for i, (clip, targets) in enumerate(val_dataloader):
            clip = torch.squeeze(clip)
            inputs = torch.Tensor(int(clip.shape[1]/opts.sample_duration) + 1, 3, opts.sample_duration,
                                  opts.sample_size, opts.sample_size)
            for k in range(inputs.shape[0] - 1):
                inputs[k, :, :, :, :] = clip[:, k * opts.sample_duration:(k + 1) * opts.sample_duration, :, :]

            inputs[-1, :, :, :, :] = clip[:, -opts.sample_duration:, :, :]

            inputs = inputs.cuda()

            outputs = model(inputs)

            pre_label = torch.sum(outputs.topk(1)[1]).item()

            if targets.item() == 0:
                if pre_label > 0:
                    acc = 0
                else:
                    acc = 1
            else:
                if pre_label > 0:
                    acc = 1
                else:
                    acc = 0

            accuracies.update(acc, 1)

            line = "Video[" + str(i) + "] :  " + "\t predict = " + str(pre_label) + "\t true = " + \
                   str(int(targets[0])) + "\t acc = " + str(accuracies.avg)
            print(line)


def main():
    opts = parse_opts()
    print(opts)

    opts.arch = '{}-{}'.format(opts.model, opts.model_depth)
    torch.manual_seed(opts.manual_seed)
    opts.input_channels = 3

    # initialize model
    print("Loading model {}.".format(opts.arch))
    model, _ = generate_model(opts)
    resume_path = opts.resume_path1
    # resuming model {}
    print("Resuming model {}.".format(resume_path))
    checkpoint = torch.load(resume_path)
    assert opts.arch == checkpoint['arch']
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    model = model.cuda()
    # initial detection model
    device = select_device()
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    weights = os.path.join(cur_dir, 'detection/best.pt')
    detect_model = attempt_load(weights, map_location=device)
    if device.type != 'cpu':
        detect_model.half()

    print("Processing case validation data.")
    val_data = globals()['{}'.format(opts.dataset)](train=2, opt=opts, detect_model=detect_model)
    val_dataloader = DataLoader(val_data, batch_size=1, shuffle=True, num_workers=opts.n_workers,
                                pin_memory=True, drop_last=False)
    print("Length of case validation dataloder = {}.".format(len(val_dataloader)))
    validation(opts, model, val_dataloader)

    print("Processing control validation data.")
    val_data_2 = globals()['{}'.format(opts.dataset)](train=3, opt=opts, detect_model=detect_model)
    val_dataloader_2 = DataLoader(val_data_2, batch_size=1, shuffle=False, num_workers=opts.n_workers,
                                  pin_memory=True, drop_last=False)
    print("Length of control validation_2 data = ", len(val_data_2))
    validation(opts, model, val_dataloader_2)


if __name__ == '__main__':
    main()

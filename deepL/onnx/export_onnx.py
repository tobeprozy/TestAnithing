import torch

class Model(torch.nn.Module):
    def __init__(self,n):
        super(Model, self).__init__()
        self.n=n
        self.conv=torch.nn.Conv2d(3,3,3)
    def forward(self,x):
        for i in range(self.n):
            x=self.conv(x)
        return x
    
if __name__ == '__main__':
    models = [Model(2),Model(3)]
    model_name=["Model_2","Model_3"]

    for model,name in zip(models,model_name):
        input = torch.randn(1, 3, 224, 224)
        model_trace=torch.jit.trace(model,input)
        model_script=torch.jit.script(model)

        torch.onnx.export(model_trace,input,"{}.onnx".format(name))
        torch.onnx.export(model_script,input,"{}_script.onnx".format(name))


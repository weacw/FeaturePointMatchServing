# Feature Point Match Serving
It is further developed based on the Opencv ORB detector. It gives the ability to match in the cloud.

# How to install?
- Execute command to install Dependent package. `install -r Sources/requirements.txt`
- Run `python http_server` and `python tcp_server`


# http_server and tcp_server?
- Http Serverr is a API to add new image
- Tcp Server is a predict and matching server

#RestFul API
###  Add new image
**Post:**
```
//form-data:
image_url:https://xxxx.com/Image.jpg
metadata:Image or json 
```

# Predict server

We use tcp protocol for image transmission.  
The image will covert to base64 encoding and send to server for predict.

- Install NetMQ or ZeroMQ

Example Code:
```C# 
 public class ImageMatchFrameRecognizerDecorator : IExpandDecorator
    {
        private bool running;
        private readonly CancellationToken cancellationToken;
        private readonly CancellationTokenSource tokenSource = new CancellationTokenSource();
        private readonly CpuImageAccessAlgorithm cpuImageAccessAlgorithm;
        private readonly Action<string> callback;
        private string metadata;

        public ImageMatchFrameRecognizerDecorator(CpuImageAccessAlgorithm _cpuImageAccessAlgorithm,
            Action<string> _callback)
        {
            cpuImageAccessAlgorithm = _cpuImageAccessAlgorithm;
            cancellationToken = tokenSource.Token;
            callback = _callback;
        }


        public async void DecoratorInvoke()
        {
            try
            {
                var tmp_ImageBytes = cpuImageAccessAlgorithm.CameraTexture.EncodeToJPG();
                var tmp_ImageBase64 = Convert.ToBase64String(tmp_ImageBytes);
                await Task.Run(() =>
                {
                    running = true;
                    tokenSource.Token.ThrowIfCancellationRequested();
                    SocketRequest(tmp_ImageBase64);
                }, cancellationToken);
            }
            catch (OperationCanceledException tmp_Exception)
            {
                Debug.LogError(
                    $"{nameof(OperationCanceledException)} throw WithOperator message:{tmp_Exception.Message}");
            }

            if (!string.IsNullOrEmpty(metadata)
                && metadata != "{}")
                callback?.Invoke(metadata);
        }

        public void DestroyDecorator()
        {
            running = false;
            tokenSource.Cancel(true);
        }


        private void SocketRequest(string _data)
        {
            // this line is needed to prevent unity freeze after one use, not sure why yet
            ForceDotNet.Force();
            using (var tmp_Client = new RequestSocket("tcp://106.14.135.205:4531"))
            {
                try
                {
                    Msg tmp_Msg = new Msg();
                    tmp_Msg.InitPool(SendReceiveConstants.DefaultEncoding.GetByteCount(_data));
                    SendReceiveConstants.DefaultEncoding.GetBytes(_data, 0, _data.Length, tmp_Msg.Data, 0);

                    if (tmp_Client.TrySend(ref tmp_Msg, TimeSpan.FromSeconds(3), false))
                    {
                        while (running)
                        {
                            if (!tmp_Client.TryReceiveFrameString(timeout: TimeSpan.FromSeconds(30),
                                out string tmp_FrameString)
                            ) continue;
                            metadata = tmp_FrameString;
                            break;
                        }
                    }
                }
                catch (TerminatingException tmp_TerminatingException)
                {
                    Debug.LogError(tmp_TerminatingException.Message);
                }
                finally
                {
                    running = false;
                    tmp_Client.Dispose();
                }
            }

            // this line is needed to prevent unity freeze after one use, not sure why yet
            NetMQConfig.Cleanup();
        }
    }
```

# Feature Point Match Serving

> Do not use for commercial projects, please obtain our authorization if necessary.

It is further developed based on the Opencv ORB detector. It gives the ability to match in the cloud.

# http_server.py and tcp_server.py?

* Http Server is a API to add new image(Http server also supports image matching)
* Tcp Server is a predict and matching server(Optional)

# How to install?

1. Install the [ `Elasticsearch` ](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html) in your server
2. Execute command to install Dependent package. `install -r Sources/requirements.txt`
3. Run `python http_server` and `python tcp_server` (Optional)

# How to depoly?
1. You need install the `Gunicorn`, use `pip install gunicorn` to install!
2. Go to the Source code folder, `gunicorn -c configure_gunicorn.py http_server:app` to run our service.

> You can make the best configuration according to your needs through the `configure_gunicorn` file.


# RestFul API

###  Add new image

**Request**

``` curl
curl --location --request POST 'http://YOUR-IP:YOUR-PORT/v1/predict_image' \
--form 'image_url=YOUR-IMAGE-URL' \
--form 'metadata=YOUR-METADATA'
```

**Response**

``` json
{
    "msg": "success"
}
```

### Remove image

**Request**

``` curl
curl --location --request DELETE 'http://YOUR-IP:YOUR-PORT/v1/predict_image' \
--form  'image_url=YOUR-IMAGE-URL'
```

**Response**

``` json
{
    "msg": "success"
}
```

### Match image

### Use network image

**Request**

``` curl
curl --location --request POST 'http://YOUR-IP:YOUR-PORT/v1/predict_image' \
--form  'image_url=YOUR-IMAGE-URL'
```

### Use Base64 image

When you are using the base64, you must remove `data:image/jpeg;base64,`
**Request**
``` curl
curl --location --request POST 'http://127.0.0.1:5000/v1/predict_image' \
--form 'image=IMAGE-BASE64-DATA'
```

**Response**

``` json
{
    "id": 0,
    "metadata": "godzilla",
    "timestamp": "2020-12-14T16:31:03.803754",
    "matchscore": 286
}
```

# TCP-Predict with C# (Optional)

We use tcp protocol for image transmission.  
The image will covert to base64 encoding and send to server for predict.

* Install NetMQ or ZeroMQ

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
            using (var tmp_Client = new RequestSocket("tcp://IP:PORT"))
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

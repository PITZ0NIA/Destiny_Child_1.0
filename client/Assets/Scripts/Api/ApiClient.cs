using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace DestinyChild.Api
{
    /// <summary>
    /// Talks to the local FastAPI server (see /server in the repo root).
    /// Plain coroutine methods - callers do StartCoroutine(ApiClient.Login(...)).
    /// No CORS concerns since this is a Standalone build, not WebGL.
    /// </summary>
    public static class ApiClient
    {
        // Change this if the server isn't running on the same machine as the client.
        public const string BaseUrl = "http://127.0.0.1:8000";

        public static IEnumerator Init(Action<InitEnvelope> onDone, Action<string> onError)
        {
            using (var req = UnityWebRequest.Get($"{BaseUrl}/api/init"))
            {
                yield return req.SendWebRequest();
                if (req.result != UnityWebRequest.Result.Success)
                {
                    onError?.Invoke(req.error);
                    yield break;
                }
                onDone?.Invoke(JsonUtility.FromJson<InitEnvelope>(req.downloadHandler.text));
            }
        }

        public static IEnumerator Login(string platformId, string displayName, Action<LoginEnvelope> onDone, Action<string> onError)
        {
            var payload = JsonUtility.ToJson(new LoginRequestBody { platform_id = platformId, display_name = displayName });
            using (var req = new UnityWebRequest($"{BaseUrl}/api/login", "POST"))
            {
                byte[] body = Encoding.UTF8.GetBytes(payload);
                req.uploadHandler = new UploadHandlerRaw(body);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");

                yield return req.SendWebRequest();
                if (req.result != UnityWebRequest.Result.Success)
                {
                    onError?.Invoke($"{req.error} ({req.downloadHandler.text})");
                    yield break;
                }
                onDone?.Invoke(JsonUtility.FromJson<LoginEnvelope>(req.downloadHandler.text));
            }
        }

        public static IEnumerator GetCatalogChildren(Action<CatalogChildrenEnvelope> onDone, Action<string> onError)
        {
            using (var req = UnityWebRequest.Get($"{BaseUrl}/api/catalog/children"))
            {
                yield return req.SendWebRequest();
                if (req.result != UnityWebRequest.Result.Success)
                {
                    onError?.Invoke(req.error);
                    yield break;
                }
                onDone?.Invoke(JsonUtility.FromJson<CatalogChildrenEnvelope>(req.downloadHandler.text));
            }
        }

        public static IEnumerator GetRoster(string sessionToken, Action<RosterEnvelope> onDone, Action<string> onError)
        {
            using (var req = UnityWebRequest.Get($"{BaseUrl}/api/roster"))
            {
                req.SetRequestHeader("X-Session-Token", sessionToken);
                yield return req.SendWebRequest();
                if (req.result != UnityWebRequest.Result.Success)
                {
                    onError?.Invoke(req.error);
                    yield break;
                }
                onDone?.Invoke(JsonUtility.FromJson<RosterEnvelope>(req.downloadHandler.text));
            }
        }

        [Serializable]
        private class LoginRequestBody
        {
            public string platform_id;
            public string display_name;
        }
    }
}

using System.Collections;
using System.Collections.Generic;
using DestinyChild.Api;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace DestinyChild
{
    /// <summary>
    /// Builds the whole UI at runtime (no hand-authored .unity scene content
    /// needed) so this drops into a brand-new empty scene with just this
    /// script on one empty GameObject. See client/README.md for setup.
    /// </summary>
    public class Bootstrap : MonoBehaviour
    {
        private Canvas _canvas;
        private GameObject _loginPanel;
        private GameObject _rosterPanel;
        private Text _statusText;
        private InputField _playerIdField;

        private void Start()
        {
            EnsureEventSystem();
            _canvas = CreateCanvas();
            BuildLoginPanel();
        }

        // ---------- flow ----------

        private void OnLoginClicked()
        {
            string playerId = string.IsNullOrWhiteSpace(_playerIdField.text) ? "player1" : _playerIdField.text.Trim();
            SetStatus("Logging in...");
            StartCoroutine(ApiClient.Login(
                playerId,
                playerId,
                onDone: envelope =>
                {
                    if (envelope.error != null)
                    {
                        SetStatus($"Login failed: {envelope.error.message}");
                        return;
                    }
                    Session.Token = envelope.data.sessionToken;
                    Session.AccountId = envelope.data.accountId;
                    Session.DisplayName = envelope.data.displayName;
                    Destroy(_loginPanel);
                    BuildRosterPanel();
                },
                onError: err => SetStatus($"Login request failed: {err}\n(Is the local server running? See server/README.md)")
            ));
        }

        private void SetStatus(string text)
        {
            if (_statusText != null) _statusText.text = text;
            Debug.Log($"[DestinyChild] {text}");
        }

        // ---------- login panel ----------

        private void BuildLoginPanel()
        {
            _loginPanel = CreatePanel(_canvas.transform, new Vector2(420, 260));

            CreateText(_loginPanel.transform, "Destiny Child - Local Server", new Vector2(0, 90), 22, TextAnchor.MiddleCenter);
            CreateText(_loginPanel.transform, "Player ID", new Vector2(-140, 30), 16, TextAnchor.MiddleLeft);

            _playerIdField = CreateInputField(_loginPanel.transform, new Vector2(0, 0), "player1");

            var loginButton = CreateButton(_loginPanel.transform, "Login", new Vector2(0, -60));
            loginButton.onClick.AddListener(OnLoginClicked);

            _statusText = CreateText(_loginPanel.transform, "", new Vector2(0, -100), 14, TextAnchor.MiddleCenter);
        }

        // ---------- roster panel ----------

        private void BuildRosterPanel()
        {
            _rosterPanel = CreatePanel(_canvas.transform, new Vector2(720, 560));

            CreateText(_rosterPanel.transform, $"Logged in as {Session.DisplayName} - Character Catalog", new Vector2(0, 260), 18, TextAnchor.MiddleCenter);

            var scrollArea = new GameObject("ScrollView", typeof(RectTransform), typeof(Image), typeof(ScrollRect), typeof(Mask));
            scrollArea.transform.SetParent(_rosterPanel.transform, false);
            var scrollRt = scrollArea.GetComponent<RectTransform>();
            scrollRt.sizeDelta = new Vector2(680, 460);
            scrollRt.anchoredPosition = new Vector2(0, -20);
            scrollArea.GetComponent<Image>().color = new Color(0, 0, 0, 0.05f);
            scrollArea.GetComponent<Mask>().showMaskGraphic = true;

            var content = new GameObject("Content", typeof(RectTransform), typeof(VerticalLayoutGroup), typeof(ContentSizeFitter));
            content.transform.SetParent(scrollArea.transform, false);
            var contentRt = content.GetComponent<RectTransform>();
            contentRt.anchorMin = new Vector2(0, 1);
            contentRt.anchorMax = new Vector2(1, 1);
            contentRt.pivot = new Vector2(0.5f, 1);
            contentRt.anchoredPosition = Vector2.zero;
            var vlg = content.GetComponent<VerticalLayoutGroup>();
            vlg.childForceExpandHeight = false;
            vlg.childForceExpandWidth = true;
            vlg.spacing = 4;
            content.GetComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;

            var scrollRect = scrollArea.GetComponent<ScrollRect>();
            scrollRect.content = contentRt;
            scrollRect.horizontal = false;
            scrollRect.vertical = true;

            SetStatus("Loading catalog...");
            StartCoroutine(ApiClient.GetCatalogChildren(
                onDone: envelope =>
                {
                    if (envelope.error != null)
                    {
                        SetStatus($"Failed to load catalog: {envelope.error.message}");
                        return;
                    }
                    PopulateRoster(content.transform, envelope.data);
                    SetStatus($"{envelope.data.Length} children loaded from the local server.");
                },
                onError: err => SetStatus($"Catalog request failed: {err}")
            ));
        }

        private void PopulateRoster(Transform content, ChildSummary[] children)
        {
            foreach (var c in children)
            {
                var row = new GameObject(c.name, typeof(RectTransform), typeof(LayoutElement));
                row.transform.SetParent(content, false);
                row.GetComponent<LayoutElement>().preferredHeight = 26;

                string line = $"{c.name}  [{new string('*', Mathf.Clamp(c.rarity, 0, 5))}]  {c.element}/{c.role}   " +
                              $"HP {c.hp}  ATK {c.atk}  DEF {c.def}  AGL {c.agl}  CRT {c.crt}";
                var text = CreateText(row.transform, line, Vector2.zero, 14, TextAnchor.MiddleLeft);
                var rt = text.rectTransform;
                rt.anchorMin = new Vector2(0, 0);
                rt.anchorMax = new Vector2(1, 1);
                rt.offsetMin = new Vector2(8, 0);
                rt.offsetMax = new Vector2(-8, 0);
            }
        }

        // ---------- generic UI helpers ----------

        private static void EnsureEventSystem()
        {
            if (FindObjectOfType<EventSystem>() != null) return;
            var es = new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
            DontDestroyOnLoad(es);
        }

        private static Canvas CreateCanvas()
        {
            var canvasGo = new GameObject("Canvas", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            var canvas = canvasGo.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvasGo.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280, 720);
            return canvas;
        }

        private static GameObject CreatePanel(Transform parent, Vector2 size)
        {
            var go = new GameObject("Panel", typeof(RectTransform), typeof(Image));
            go.transform.SetParent(parent, false);
            var rt = go.GetComponent<RectTransform>();
            rt.sizeDelta = size;
            rt.anchoredPosition = Vector2.zero;
            go.GetComponent<Image>().color = new Color(0.1f, 0.1f, 0.12f, 0.95f);
            return go;
        }

        private static Font DefaultFont()
        {
            var f = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            return f != null ? f : Resources.GetBuiltinResource<Font>("Arial.ttf");
        }

        private static Text CreateText(Transform parent, string content, Vector2 pos, int fontSize, TextAnchor anchor)
        {
            var go = new GameObject("Text", typeof(RectTransform), typeof(Text));
            go.transform.SetParent(parent, false);
            var rt = go.GetComponent<RectTransform>();
            rt.sizeDelta = new Vector2(360, 30);
            rt.anchoredPosition = pos;
            var text = go.GetComponent<Text>();
            text.text = content;
            text.font = DefaultFont();
            text.fontSize = fontSize;
            text.alignment = anchor;
            text.color = Color.white;
            text.horizontalOverflow = HorizontalWrapMode.Overflow;
            return text;
        }

        private static InputField CreateInputField(Transform parent, Vector2 pos, string placeholder)
        {
            var go = new GameObject("InputField", typeof(RectTransform), typeof(Image), typeof(InputField));
            go.transform.SetParent(parent, false);
            var rt = go.GetComponent<RectTransform>();
            rt.sizeDelta = new Vector2(280, 30);
            rt.anchoredPosition = pos;
            go.GetComponent<Image>().color = new Color(1, 1, 1, 0.9f);

            var textGo = new GameObject("Text", typeof(RectTransform), typeof(Text));
            textGo.transform.SetParent(go.transform, false);
            var textRt = textGo.GetComponent<RectTransform>();
            textRt.anchorMin = Vector2.zero;
            textRt.anchorMax = Vector2.one;
            textRt.offsetMin = new Vector2(8, 4);
            textRt.offsetMax = new Vector2(-8, -4);
            var text = textGo.GetComponent<Text>();
            text.font = DefaultFont();
            text.fontSize = 16;
            text.color = Color.black;
            text.alignment = TextAnchor.MiddleLeft;

            var field = go.GetComponent<InputField>();
            field.textComponent = text;
            field.text = placeholder;
            return field;
        }

        private static Button CreateButton(Transform parent, string label, Vector2 pos)
        {
            var go = new GameObject("Button", typeof(RectTransform), typeof(Image), typeof(Button));
            go.transform.SetParent(parent, false);
            var rt = go.GetComponent<RectTransform>();
            rt.sizeDelta = new Vector2(160, 36);
            rt.anchoredPosition = pos;
            go.GetComponent<Image>().color = new Color(0.25f, 0.45f, 0.85f);

            CreateText(go.transform, label, Vector2.zero, 16, TextAnchor.MiddleCenter).color = Color.white;

            return go.GetComponent<Button>();
        }
    }
}

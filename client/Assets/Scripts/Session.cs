namespace DestinyChild
{
    /// <summary>Holds the current login session in memory for the run.</summary>
    public static class Session
    {
        public static string Token;
        public static int AccountId;
        public static string DisplayName;

        public static bool IsLoggedIn => !string.IsNullOrEmpty(Token);

        public static void Clear()
        {
            Token = null;
            AccountId = 0;
            DisplayName = null;
        }
    }
}

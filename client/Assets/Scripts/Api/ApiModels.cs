using System;
using System.Collections.Generic;

namespace DestinyChild.Api
{
    // Concrete (non-generic) DTOs per endpoint - Unity's JsonUtility does not
    // reliably support generic [Serializable] types across Unity versions,
    // so each response shape gets its own class instead of a shared
    // Envelope<T>. Mirrors server/app/schemas.py's ok()/fail() envelope.

    [Serializable]
    public class ErrorBody
    {
        public string code;
        public string message;
    }

    [Serializable]
    public class LocalTimeInfo
    {
        public string serverTime;
    }

    [Serializable]
    public class InitData
    {
        public string serverStatus;
        public bool maintenance;
        public string minClientVersion;
        public string serverTime;
    }

    [Serializable]
    public class InitEnvelope
    {
        public InitData data;
        public ErrorBody error;
        public LocalTimeInfo localTimeInfo;
    }

    [Serializable]
    public class ProfileData
    {
        public int level;
        public int exp;
        public int gold;
        public int gems;
    }

    [Serializable]
    public class LoginData
    {
        public int accountId;
        public string displayName;
        public string sessionToken;
        public string expiresAt;
        public ProfileData profile;
    }

    [Serializable]
    public class LoginEnvelope
    {
        public LoginData data;
        public ErrorBody error;
        public LocalTimeInfo localTimeInfo;
    }

    [Serializable]
    public class ChildSummary
    {
        public int id;
        public string name;
        public int rarity;
        public string element;
        public string role;
        public int hp;
        public int atk;
        public int def;
        public int agl;
        public int crt;
    }

    // JsonUtility can't parse a bare top-level array, and the server wraps
    // it in {"data": [...]} anyway, but JsonUtility also can't deserialize a
    // List<T>/T[] that sits directly as the envelope's "data" field name
    // when the field itself needs a custom wrapper for arrays at the root of
    // that field - a plain public ChildSummary[] data; works fine here since
    // it's a *named* field, not the JSON root.
    [Serializable]
    public class CatalogChildrenEnvelope
    {
        public ChildSummary[] data;
        public ErrorBody error;
        public LocalTimeInfo localTimeInfo;
    }

    [Serializable]
    public class RosterEntry
    {
        public int playerChildId;
        public int level;
        public int stars;
        public int exp;
        public ChildSummary child;
    }

    [Serializable]
    public class RosterEnvelope
    {
        public RosterEntry[] data;
        public ErrorBody error;
        public LocalTimeInfo localTimeInfo;
    }
}

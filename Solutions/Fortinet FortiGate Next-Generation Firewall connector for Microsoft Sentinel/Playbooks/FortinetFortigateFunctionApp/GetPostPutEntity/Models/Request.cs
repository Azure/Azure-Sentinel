public class Member
    {
        public string name { get; set; }
        public string q_origin_key { get; set; }
    }

    public class Root
    {
        public string name { get; set; }
        public Member member { get; set; }
    }
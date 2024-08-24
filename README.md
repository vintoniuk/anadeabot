# AnadeaBot

A minimalistic T-shirt design bot.

- possibility of automatic change of design options if user opinions change

- train LittleLlama model with knowledge distillation tuned specifically for dialogue about T-shirts

- track user profile and preferences, and truncate the history when necessary

- add user personality analysis for generation of the most appropriate T-shirt designs

---

Features:

- make an order and design a T-shirt

- answer user questions using FAQ (retrieval)

- send support requests

---

Routing:

- check whether a user is ready to make an order and ask for confirmation

- check whether a user needs help from FAQ

- check whether a user faced an unpredictable situation and needs help from the support team

---

Dialogue:

A: Hi! Would you like to design and order your personal T-shirt?

U: Yes. Let's do that.

A:  What color would you like to choose?

U: Probably red? Would it be great?

A: Yes, it is exactly the best. And what size would you like to choose?

U: 

---

Plan:

- greeting

- ask for color

- ask for size

- ask for style

- ask for gender

- ask for printing options

- compose an order and ask for confirmation

---

#### TODO

- add custom color
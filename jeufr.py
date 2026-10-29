import json
import os

FILENAME = "questions.json"


def load_questions():
  if os.path.exists(FILENAME):
    with open(FILENAME, "r", encoding="utf-8") as f:
      return json.load(f)
  return []


def save_questions(questions):
  with open(FILENAME, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=4)


def teacher_mode():
  print("\n--- 👨‍🏫 Mode Enseignant (Ajouter des questions) ---")
  q = input("Entrez la question : ")
  options = []
  for i in range(3):
    opt = input(f"Entrez l'option numéro {i+1} : ")
    options.append(opt)

  try:
    ans = int(input("Numéro de la bonne réponse (1, 2 ou 3) : ")) - 1
    questions = load_questions()
    questions.append({"question": q, "options": options, "answer": ans})
    save_questions(questions)
    print("✅ Question enregistrée avec succès dans le fichier !")
  except ValueError:
    print("❌ Veuillez entrer un numéro valide.")


def student_mode():
  questions = load_questions()
  if not questions:
    print(
        "\n⚠️ Aucune question enregistrée pour le moment. Demandez à"
        " l'enseignant d'en ajouter."
    )
    return

  score = 0
  print("\n--- 🎮 Mode Élève (Commencer le Quiz) ---")
  for idx, q_data in enumerate(questions, 1):
    print(f"\nQuestion {idx}: {q_data['question']}")
    for i, opt in enumerate(q_data["options"]):
      print(f"{i+1}. {opt}")

    try:
      ans = int(input("Choisissez le numéro de la bonne réponse : ")) - 1
      if ans == q_data["answer"]:
        print("🌟 Bonne réponse ! Bravo.")
        score += 1
      else:
        print("❌ Mauvaise réponse.")
    except ValueError:
      print("❌ Entrée invalide !")

  print(
      f"\n🎉 Quiz terminé ! Votre score final est de : {score} sur"
      f" {len(questions)}"
  )


def main():
  while True:
    print("\n=== Système de Quiz Éducatif ===")
    print("1. Mode Enseignant (Ajouter des questions)")
    print("2. Mode Élève (Jouer au quiz)")
    print("3. Quitter")
    choice = input("Choisissez une option (1, 2 ou 3) : ")

    if choice == "1":
      teacher_mode()
    elif choice == "2":
      student_mode()
    elif choice == "3":
      print("Au revoir et bon courage pour vos études !")
      break
    else:
      print("❌ Choix invalide, réessayez.")


if __name__ == "__main__":
  main()
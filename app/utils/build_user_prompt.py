def _build_user_prompt(resume_text: str, extracted_links: list[str]) -> list[str]:
    links_section = ""
    if extracted_links:
        links_section = (
            "\n\nHYPERLINKS EMBEDDED IN THE PDF (use these for the links fields):\n"
            + "\n".join(f"- {l}" for l in extracted_links)
        )

    return (
        f"Parse the following resume and return the structured JSON.\n"
        f"{links_section}\n\n"
        f"RESUME TEXT:\n{resume_text}"
    )

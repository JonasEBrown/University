export default function ParseText(text: string): React.ReactElement {
	let current: string = "";
	let parsedText = [];
	while (text.length > 0) {
		let char: string = text[0];
		text = text.slice(1);
		if (char == "<") {
			parsedText.push(current);
			current = "";
			while (text.length > 0 && char !== ">") {
				char = text[0];
				text = text.slice(1);
				if (char !== ">") current += char;
			}
			const tag: string = current;
			current = "";
			const end: number = text.indexOf(`</${tag}>`);
			if (end > 0) {
				current = text.slice(0, end);
				text = text.slice(end + tag.length + 3);
				console.log(current, text);
			} else
				return (
					<b color="red">{`No closing tag to "<${tag}>" in "${text}"!`}</b>
				);
			const processedInnerText = ParseText(current);
			switch (tag) {
				case "b":
					parsedText.push(
						<b key={parsedText.length}>{processedInnerText}</b>
					);
					break;
				default:
					return <b color="red">{`Unknown tag "<${tag}>"!`}</b>;
			}
			current = "";
		} else current += char;
	}
	if (current !== "") parsedText.push(current);
	if (parsedText.length === 1) return <>{parsedText[0]}</>;
	return <p>{parsedText}</p>;
}

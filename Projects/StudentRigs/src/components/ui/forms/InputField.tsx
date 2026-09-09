export default function Input({
	name,
	type,
	label,
	placeholder,
	value,
	onChange,
	min,
	className,
	...props
}: {
	name: string;
	type?: string;
	label?: string;
	placeholder?: string;
	value?: string;
	onChange?: (value: string) => void;
	min?: number;
	className?: string;
	[key: string]: any;
}) {
	return (
		<div className="flex flex-col">
			{label && <div className="text-sm font-medium mb-1.5">{label}</div>}
			<input
				type={type}
				id={name}
				name={name}
				min={min}
				placeholder={placeholder}
				value={value}
				onChange={(e) => {
					if (onChange) onChange(e.target.value);
				}}
				className={`input-field ${className}`}
				{...props}
			/>
		</div>
	);
}

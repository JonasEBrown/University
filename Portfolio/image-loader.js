
export default ({ src, width, height }) => {
    return src.replace(`/${process.env.GITHUB_REPO}`, '');
}
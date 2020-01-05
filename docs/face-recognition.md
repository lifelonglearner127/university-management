## Face Recognition

### Most popular algorithms
- Eigenfaces
    - This method was proposed in 1987. It relies on Pricipal Component Analysis.
    - Given a dataset of face images, we apply eigenvalue decomposition of the dataset, keeping the eigenvectors with the largest corresponding eigenvalues.
    - Given these eigenvectors, a face can then be represented as a linear combination of eigenfaces.
    - Face detection can be performed by computing `Euclidean` distance between the eigenfaces representations.

- LBPs
    - This method was proposed in 2006. It relies on feature extractions using Local Binary Pattern.
    - By dividing the image into cells we can introduce locality into the final feature vector.
    - Some cells are weighted such that they contribute more to the overall representation. Cells in the corners carry less identifying facial information compared to the cells in the center of the grid.
    - Finally concentrate the weighted LBP histograms to for our final feature vector
    - Face detection can be performed by k-NN classification using `Chi-square` distance between the query image and the dataset of labeled faces.
        > Since we are computing histogram, `Chi-square` distance is better choice than `Euclidean` distance

- LBP vs. Eigenfaces

    Eigenfaces algorithms requires that all faces to be identified be present at training time. This means that if a new face is added to the dataset, the entire Eigenfaces classifier has to be retrained which can be quite computationally intensive. Instead, the LBPs for face recognition algorithm can simply insert new face samples without having re-trained at all.


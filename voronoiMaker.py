import math as m
import pygame
import pygame.gfxdraw
pygame.init()
screenSize = (800, 800)
screen = pygame.display.set_mode(screenSize)
clock = pygame.time.Clock() 
framerate=30

points = []
for i in range(2):
    for j in range(2):
        points.append([screenSize[0]*i, screenSize[1]*j])

boundaries = ((0, 1), (1, 3), (3, 2), (2, 0)) # out of order because the order of corner points is out of order
seeds = []
regions = []

def lineIntersection(line1, line2): # list of positions, list of positions
    xDiff1 = line1[0][0]-line1[1][0]
    yDiff1 = line1[0][1]-line1[1][1]
    xDiff2 = line2[0][0]-line2[1][0]
    yDiff2 = line2[0][1]-line2[1][1]
    denom = xDiff1*yDiff2 - xDiff2*yDiff1
    if denom == 0:
        return None
    coord = lambda a,b: ((line1[0][0]*line1[1][1] - line1[0][1]*line1[1][0])*a - (line2[0][0]*line2[1][1] - line2[0][1]*line2[1][0])*b)//denom
    return [coord(xDiff2, xDiff1), coord(yDiff2, yDiff1)]

def createRegions(points, seeds, boundaries): # list of positions, list of indices, list of index pairs
    '''
    points is a list of lists, each sublist contains two integers for x and y coordinates
    the first n points in 'points' are the boundary points (where n+1 is the length of 'boundaries')
    '''
    regions = []
    for i in range(len(seeds)):
        bisections = [] # [x1, y1, x2, y2]
        for line in boundaries:
            bisections.append([[points[line[0]][0], points[line[0]][1]], [points[line[1]][0], points[line[1]][1]]])

        for j in range(len(seeds)):
            if i==j:
                continue
            line = [[0, 0], [0, 0]]
            line[0][0] = (points[seeds[i]][0]+points[seeds[j]][0])//2
            line[0][1] = (points[seeds[i]][1]+points[seeds[j]][1])//2
            vector = [points[seeds[j]][0]-points[seeds[i]][0], points[seeds[j]][1]-points[seeds[i]][1]]
            line[1][0] = line[0][0]-vector[1]
            line[1][1] = line[0][1]+vector[0]
            bisections.append([line[0].copy(), line[1].copy()])

        intersections = []
        intersection_indices = []
        for j in range(len(bisections)):
            for k in range(j+1, len(bisections)):
                intersection = lineIntersection(bisections[j], bisections[k])
                if intersection and abs(intersection[0])+abs(intersection[1]) <= screenSize[0]+screenSize[1]:
                    intersections.append(intersection)
                    intersection_indices.append([j, k])

        regionPoints = []
        for j, point in enumerate(intersections):
            closest = True
            for k in range(len(bisections)):
                if k in intersection_indices[j]:
                    continue
                intersection = lineIntersection([point, points[seeds[i]]], bisections[k])

                if intersection and abs(intersection[0])+abs(intersection[1]) <= screenSize[0]+screenSize[1]:
                    d1 = (point[0]-points[seeds[i]][0])**2 + (point[1]-points[seeds[i]][1])**2
                    d2 = (intersection[0]-points[seeds[i]][0])**2 + (intersection[1]-points[seeds[i]][1])**2
                    d3 = (point[0]-intersection[0])**2 + (point[1]-intersection[1])**2
                    if d2 < d1 and d3 < d1:
                        closest = False
                        break
            if closest:
                regionPoints.append(point)

        angle = lambda point: m.atan2(point[1]-points[seeds[i]][1], point[0]-points[seeds[i]][0])
        regionPoints = sorted(regionPoints, key=angle)
        regions.append(regionPoints)
    return regions

done=False
while not done:
    clock.tick(framerate)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            done=True
        if event.type == pygame.MOUSEBUTTONUP:
            seeds.append(len(points))
            points.append([event.pos[0], event.pos[1]])
            regions = createRegions(points, seeds, boundaries)

    screen.fill((0, 0, 0))

    for i in range(len(regions)):
        pygame.gfxdraw.filled_polygon(screen, regions[i], [255/len(regions)*i]*3)

    for seed in seeds:
        pygame.gfxdraw.circle(screen, points[seed][0], points[seed][1], 5, (255, 0, 0))
    pygame.display.flip()